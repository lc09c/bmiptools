===================
Plugin installation
===================


bmiptools come with a series of plugins. However any user can develop its own plugin, and by following the guidelines
described in the section :doc:`plugin structure`, compatibility with the bmiptools ecosystem is ensured. Once that a
new plugin has been developed, to integrate it in bmiptools one need to install it. In this way:

* the new plugin will be available in the GUI;
* the new plugin will be available for the creation of pipeline object;
* the new plugin can be imported in a simplified way.


Add and use a new plugin
========================


The development of a new plugin means that the user created some file ``my_plugin.py`` where the plugin is contained
in a suitable class ``MyPlugin``. Assuming that the file ``my_plugin.py`` can be found at the path
``../[...]/my_plugin.py``, to install a plugin it is enough run the two lines of code below.

.. code-block::

   from bmiptools.setting.configure import install_plugin


   install_plugin(r'../[...]/my_plugin.py','MyPlugin')


The function :py:func:`install_plugin <bmiptools.setting.configure.install_plugin>` takes two arguments: the path to the
python script containing plugin class, and the name of the plugin class (which is also considered the name of the
plugin). The installation of a plugin is clearly meant to be done just one time for each new plugin: simply add this file
to the list of files that are imported when bmiptools is used, making the new plugin always available.

.. attention::

   Since once installed, bmiptools will always assumes to find the plugin file at the path specified at the moment of
   plugin installation. If this file is moved or eliminated a warning message will be rised and the corresponding plugin
   cannot be anymore used.

Once that the plugin has been installed, it can be imported in a simplified manner. Indeed the plugin class will be
stored both in the ``PLUGINS`` and in the ``LOCAL_PLUGINS`` dictionaries. Both of them can be easily imported from
:py:mod:`bmiptools.setting.installed_plugins`.


.. code-block::

   from bmiptools.setting.installed_plugins import LOCAL_PLUGINS     # import all local plugins

   print(LOCAL_PLUGINS)


Remove a plugin
===============

Any *local* plugin can be uninstalled. This can be done with the method
:py:func:`uninstall_plugin <bmiptools.setting.configure.uninstall_plugin>` simpy specifying the name of the plugin to
uninstall.


.. code-block::

   from bmiptools.setting.configure import uninstall_plugin

   uninstall_plugin('MyPlugin')


With the code above the uninstalled plugin will not be loaded anymore and therefore removed from the ``PLUGINS`` and
``LOCAL_PLUGINS`` dictionary (therefore it cannot be used in a pipeline and in the GUI).