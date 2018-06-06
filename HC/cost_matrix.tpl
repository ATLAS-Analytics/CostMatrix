Job (
 name = '' ,
 outputsandbox = [] ,
 info = JobInfo (
    ) ,
 inputdata = None , 
 merger = None ,
 inputsandbox = [ ] ,
 application = Athena (
    collect_stats = True ,
    atlas_environment = [] ,
    atlas_release = '17.6.0' ,
    atlas_project = '' ,
    exclude_package = [] ,
    atlas_production = '' ,
    options = '%IN' ,
    atlas_use_AIDA = False ,
    atlas_cmtconfig = 'i686-slc5-gcc43-opt',
    max_events = -999 ,
    exclude_from_user_area = [] ,
    atlas_run_dir = './' ,
    atlas_exetype = 'EXE' ,
    athena_compile = False ,
    trf_parameter = {} ,
    atlas_run_config = {'input': {}, 'other': {}, 'output': {}} ,
    option_file = [ File (
		name = '####JOBOPTIONS####' ,       
		subdir = '.'
       ) , ] ,
    group_area = File (
    name = '' ,
    subdir = '.'
    ) ,
    user_area = File (
       name = '####USERAREA####' ,
       subdir = '.'
    ) 
    ) ,
 outputdata = DQ2OutputDataset (
   datasetname = '####OUTPUTDATASETNAME####',  
   outputdata = ['info.txt'] ,
   local_location = '' ,
   location = ''
 ) ,
 splitter = GenericSplitter (
   attribute = 'comment' ,
   values = [ '42' ]
  ) ,
 backend = Panda (
    nobuild = True ,
    site = ####SITES#### ,
    accessmode = '####INPUTTYPE####' ,
    requirements = PandaRequirements (
	enableJEM = False ,
       	configJEM = '+debug'
	)
    )  
 ) 
