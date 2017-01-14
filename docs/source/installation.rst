.. _installation:

=================================
Installation and getting started
=================================

To install ViXeN, you first need to know the platform you will be running it on.
ViXeN is available for Linux (64 bit), Mac (64 bit), and Windows (32 and 64 bit).

In order to use ViXeN you will need to have a working browser. See the
:ref:`dependencies` section for more information on the dependencies.
Installing ViXeN is relatively straight-forward. Please see the instructions
for installing ViXeN in the relevant sections below.

.. contents::
    :local:
    :depth: 1

.. _dependencies:

------------------
Dependencies
------------------

^^^^^^^^^^^^^^^^^^
Core dependencies
^^^^^^^^^^^^^^^^^^

Please make sure you have a good, functional browser such as:
- Mozilla Firefox (any recent version)
- Google Chrome (any recent version)
- Internet Explorer (IE 9 and above)


^^^^^^^^^^^^^^^^^^^^^^
Optional dependencies
^^^^^^^^^^^^^^^^^^^^^^

The optional dependencies are:

- ffmpeg_

.. _ffmpeg: http://ffmpeg.org


This is only needed if you wish to use ffmpeg to convert any of your video media.

-------------------------------
Installing ViXeN on GNU/Linux
-------------------------------

On GNU/Linux systems one may install the dependencies by following three very
simple steps:

- Download the `ViXeN binary`_ for Linux.
- Unpack the ``vixen*.tgz`` file.
- Run the application inside the unpacked directory.

More detailed instructions are given below.

.. _ViXeN binary: https://github.com/prabhuramachandran/vixen/releases

.. _using-nautilus:

^^^^^^^^^^^^^^^^^^^
Using Nautilus
^^^^^^^^^^^^^^^^^^^

1. Download the ViXen binary file (say vixen-0.5-linux64.tgz) from
   `ViXeN binary`_ to your preferred directory.


2. Right click and select 'Extract Here' or 'Open With Archive Manager'. A
   ViXeN folder will appear in the directory you have selected (in this case
   the folder will be ``vixen-0.5``).

3. Open the directory and double click the ``vixen`` file. The ViXeN
   application will open on the browser, **if** Nautilus supports running
   executables. If it does not, run the command shown in :ref:`using-cli`.

.. _using-cli:

^^^^^^^^^^^^^^^^^^^^^^^
Using the Command Line
^^^^^^^^^^^^^^^^^^^^^^^

After downloading and unpacking ViXen either :ref:`using-nautilus`, run the
following commands on the terminal::

	$ cd vixen-0.5

Where ``vixen-0.5`` is the extracted ViXeN binary. Suppose you downloaded and
unpacked the ``vixen-0.5-linux64.tgz`` file in a folder named ``Software`` in
your ``home`` directory, then this command will be::

	$ cd Software/vixen-0.5

Then run the application using::

	$ ./vixen


------------------------------
Installing ViXeN on Mac OS X
------------------------------

1. On OS X, download the ZIP file.
2. Unpack it.
3. Run the resulting dmg file by double clicking it.

You may move this dmg file anywhere you like or move it to your
``Applications`` folder if you wish to.

------------------------------
Installing ViXeN on Windows
------------------------------


1. On Windows, download the ZIP file for your platform.
2. Unpack the ZIP file.
3. Inside the unpacked directory is a ``vixen.bat`` script or a ``vixen.lnk``
   shortcut that you can use to run the application.

The application will open in your default browser window.