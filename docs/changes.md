volkanic: changes
-----------------

### 0.6.0 -- plan
- require Python 3.6+

### 0.5.0 -- plan
- remove `GlobalInterface.{_split_name,jinja2_env,_get_conf_search_paths}`
- add `environ.PathType`

### 0.4.2
- add GI.package_dir, GI.project_dir 
- rename GlobalInterfaceTrial => GlobalInterfaceTribal
- python_requires: ">=3.5"
- unrequire pyyaml 
- add GlobalInterface.namespaces
- add utils.under_home_dir_hidden()
- ErrorInfo.iter_related_files()
- utils.guess_content_type()

### 0.4.1
- remove GIMixinDirs
- CommandOptionDict: _expand, _explode

### 0.4.0
- remove CommandConf
- remove volkanic.default

### 0.3.6 
- add utils.load_json5_file()
- add utils.discard_arguments()
- add GlobalInterface._options
