import datetime
import json
import os
from os.path import (abspath, basename, dirname, exists, expanduser, isdir,
                     join, realpath, splitext)
import re
import shutil

from traits.api import (Any, Dict, Enum, HasTraits, Instance, List, Long,
                        Property, Str)

from .media import Media
from .directory import Directory
from . import processor


def get_project_dir():
    d = expanduser(join('~', '.vixen'))
    if not isdir(d):
        os.makedirs(d)
    return d

def get_file_saved_time(path):
    dt = datetime.datetime.fromtimestamp(os.stat(path).st_ctime)
    return dt.ctime()


class TagInfo(HasTraits):
    name = Str
    type = Enum("string", "int", "float", "bool")
    default = Any

    def _default_default(self):
        map = {"string": "", "int": 0, "float": 0.0, "bool": False}
        return map[self.type]


def open_file(fname_or_file, mode='r'):
    if hasattr(fname_or_file, 'read'):
        return fname_or_file
    else:
        return open(fname_or_file, mode)

def sanitize_name(name):
    name = name.lower()
    name = re.sub(r'\s+', '_', name)
    return re.sub(r'\W+', '', name)

def get_non_existing_filename(fname):
    if exists(fname):
        base, ext = splitext(basename(fname))
        return join(dirname(fname), base +'_a' + ext)
    else:
        return fname


class Project(HasTraits):
    name = Str
    description = Str
    path = Str
    root = Instance(Directory)
    tags = List(TagInfo)

    media = Dict(Str, Media)

    extensions = List(Str)

    processors = List(processor.FactoryBase)

    number_of_files = Long

    # Path where the project data is saved.
    save_file = Str

    last_save_time = Str

    def add_tags(self, tags):
        tags = list(self.tags) + tags
        self.update_tags(tags)

    def update_tags(self, new_tags):
        old_tags = self.tags
        new_tag_names = set(tag.name for tag in new_tags)
        tag_info = dict((tag.name, tag.type) for tag in old_tags)
        removed = []
        added = []
        for tag in new_tags:
            if tag.name not in tag_info:
                added.append(tag)
            elif tag_info[tag.name] != tag.type:
                removed.append(tag)
                added.append(tag)
        for tag in old_tags:
            if tag.name not in new_tag_names:
                removed.append(tag)
        self.tags = new_tags

        for m in self.media.values():
            for tag in removed:
                del m.tags[tag.name]
            for tag in added:
                m.tags[tag.name] = tag.default

    def export_csv(self, fp, cols=None):
        """Export metadata to a csv file.  If `cols` are not specified,
        it writes out all the useful metadata.

        Parameters
        -----------

        path: str: a path to the csv file to dump.
        cols: sequence: a sequence of columns to write.
        """
        lines = []
        data = []
        all_keys = set()
        for key in sorted(self.media.keys()):
            item = self.media[key]
            d = item.flatten()
            all_keys.update(d.keys())
            data.append(d)
        if cols is None:
            cols = all_keys
            cols = list(sorted(cols))
        # Write the header.
        lines.append(','.join(cols))
        # Assemble the lines.
        for d in data:
            line = []
            for key in cols:
                elem = d[key]
                if isinstance(elem, basestring):
                    elem = '"%s"'%elem
                else:
                    elem = str(elem) if elem is not None else ""
                line.append(elem)
            lines.append(','.join(line))

        # Write it out.
        of = open_file(fp, 'w')
        for line in lines:
            of.write(line +'\n')
        of.close()

    def load(self, fp=None):
        """Load media info from opened file object.
        """
        if fp is None:
            if not exists(self.save_file):
                return
            fp = open_file(self.save_file)
        else:
            fp = open_file(fp)

        data = json.load(fp)
        fp.close()
        self.name = data.get('name', '')
        self.description = data.get('description', '')
        self.path = data.get('path')
        self.tags = [TagInfo(name=x[0], type=x[1]) for x in data['tags']]
        self.processors = [processor.load(x)
                           for x in data.get('processors', [])]
        media = dict((key, Media(**kw)) for key, kw in data['media'])
        # Don't send object change notifications when this large data changes.
        self.trait_setq(media=media)
        root = Directory()
        root.__setstate__(data.get('root'))
        self.extensions = root.extensions
        self.root = root
        self.number_of_files = len(self.media)
        # This is needed as this is what makes the association from the media
        # to the file.
        self.scan()

    def save(self):
        """Save current media info to a file object
        """
        if len(self.save_file) > 0:
            self.save_as(self.save_file)
            self._update_last_save_time()
        else:
            raise IOError("No valid save file set.")

    def save_as(self, fp):
        """Save copy to specified path.
        """
        fp = open_file(fp, 'w')
        media = [(key, m.to_dict()) for key, m in self.media.items()]
        tags = [(t.name, t.type) for t in self.tags]
        root = self.root.__getstate__()
        processors = [processor.dump(x) for x in self.processors]
        data = dict(
            version=1, path=self.path, name=self.name,
            description=self.description, tags=tags, media=media,
            root=root, processors=processors
        )
        json.dump(data, fp)
        fp.close()

    def scan(self, refresh=False):
        """Find all the media recursively inside the root directory.
        This will not clobber existing records but will add any new ones.
        """
        media = self.media
        new_media = {}
        self._setup_root()
        default_tags = dict((ti.name, ti.default) for ti in self.tags)
        def _scan(dir):
            for f in dir.files:
                m = media.get(f.relpath)
                if m is None:
                    m = self._create_media(f, default_tags)
                    new_media[f.relpath] = m
                f.media = m
            for d in dir.directories:
                if refresh:
                    d.refresh()
                _scan(d)
        if refresh:
            self.root.refresh()
        _scan(self.root)
        if len(new_media) > 0:
            # This is done because if media is changed, a trait change notify
            # will be sent to listeners with a very large amount of data
            # potentially.  The jigna webserver will marshal all the keys
            # and not be able to send the information.
            media_copy = dict(media)
            media_copy.update(new_media)
            self.trait_setq(media=media_copy)
            self.number_of_files = len(self.media)

    def refresh(self):
        self.scan(refresh=True)

    ##### Private protocol ################################################

    def _create_media(self, f, default_tags):
        m = Media.from_path(f.path)
        m.tags = dict(default_tags)
        return m

    def _setup_root(self):
        path = abspath(expanduser(self.path))
        root = self.root
        if root is None or realpath(root.path) != realpath(path):
            self.root = Directory(path=path, extensions=self.extensions)

    def _tags_default(self):
        return [TagInfo(name='completed', type='bool')]

    def _save_file_default(self):
        if len(self.name) > 0:
            fname = sanitize_name(self.name) + '.vxn'
            d = get_project_dir()
            return get_non_existing_filename(join(d, fname))
        else:
            return ''

    def _update_last_save_time(self):
        self.last_save_time = get_file_saved_time(self.save_file)

    def _last_save_time_default(self):
        if exists(self.save_file):
            return get_file_saved_time(self.save_file)

    def _name_changed(self, name):
        if len(name) > 0:
            old_save_file = self.save_file
            old_dir = dirname(old_save_file)
            new_save_file = join(old_dir, sanitize_name(name) + '.vxn')
            if new_save_file != old_save_file:
                self.save_file = new_save_file
                if exists(old_save_file):
                    shutil.move(old_save_file, self.save_file)

    def _extensions_changed(self, ext):
        if self.root is not None:
            self.root.extensions = ext

    def _extensions_items_changed(self):
        if self.root is not None:
            self.root.extensions = self.extensions