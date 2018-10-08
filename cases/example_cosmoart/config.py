import os
import types


user = os.environ['USER']
mail_address = {
    'gkuhl':     'gerrit.kuhlmann@empa.ch',
    'kug':       'gerrit.kuhlmann@empa.ch',
    'dbrunner':  'dominik.brunner@empa.ch',
    'haussaij':  'jean-matthieu.haussaire@empa.ch',
    'mjaehn':    'michael.jaehn@empa.ch',
    'muq':       'qing.mu@empa.ch',
    'parsenov' : 'pavle.arsenovic@empa.ch',
    'ochsnerd' : 'david.ochsner@empa.ch',
}[user]


# Everything defined before is not written to os.environ
# and thus not available to bash scripts.
not_config = list(locals().keys())

compute_host = 'daint'
compute_queue = 'debug' #'debug' #'normal'
compute_account = 'em05' #'pr04'

# Controls which flavour of cosmo is used to do the simulation. Has to be either 'comso' or 'cosmoart'
# If omitted, will default to 'cosmo'
target = 'cosmoart'

# case name = pathname in cases/
path = os.path.realpath(__file__)
casename = os.path.basename(os.path.dirname(path)) 

# input root
input_root = '/store/empa/em05/input_cosmoart_processing_chain_example/'

# output
output_root = os.environ['SCRATCH'] + "/cosmoart_processing_chain/output/" + casename

# working root
work_root = os.environ['SCRATCH'] + "/cosmoart_processing_chain"
log_dir = os.path.join(work_root, 'logs')

# anthropogenic emissions pre-processed for mother and nested domain
emissions_dir = os.path.join(input_root, 'emissions_mother_MACC')
emis_gridname = "macc_"

# ifs_hres_bc files
ifs_hres_dir = os.path.join(input_root, 'ifs_hres_bc')
ifs_hres_inc = 3  # increment between timesteps
ifs_basename = "eas"

# photolysis-rate file
photo_rate_file = os.path.join(input_root, 'art_photolysis', 'papa_data.p')

# obs_nudging files
obs_nudging_dir = os.path.join(input_root, 'obs_nudging')
# nudging-filename: obs_nudging_prefix +
#                   sim_date.strftime(obs_nudging_date_format) +
#                   (sim_date + timedelta(days=1).strftime(obs_nudging_date_format)
# Example: obs_nudging temp for simulation on 4.2.15:
#          cdfin_temp-20150204000000-20150205000000
obs_nudging_prefixes = ['cdfin_amdar', 'cdfin_buoy', 'cdfin_pilot_p',
                        'cdfin_ship', 'cdfin_synop', 'cdfin_temp',
                        'cdfin_wprof']
obs_nudging_date_format = "-%Y%m%d%H%M%S"


# ICBC
# if the data is already preprocessed and just need to be copied, 
# - mozart_file_orig is not used
# - mozart_dir_proc is where your data to be copied is
mozart_file_orig = os.path.join(input_root, 'icbc', 'mozart4geos5_20150203-20150221.nc')
mozart_dir_proc = os.path.join(input_root, 'icbc', 'processed')
mozart_inc = 6 # increment between timesteps, not sure if this can be changed even
mozart_prefix = 'mozart'

# chain root (TODO: remove)
chain_src_dir = os.getcwd()
tools_dir = os.path.join(chain_src_dir, 'jobs/tools')

# some constants for scripts
del_tmp_timeout = 120   # timeout in days after which temporary files 
                        # like restarts (last forecast hour of day - 1) are removed
                        # by "purgetmp"

meteo_spinup = 0        # time in hours the model is integrated before transport simulation 
                        # is started (i.e. spinupstart = inidate - meteospinup)
                        # NOTE: has to be multiple of meteo increment (e.g 3hrs for IFS)

# INT2LM
int2lm_extpar_dir = os.path.join(input_root, 'extpar')
int2lm_extpar_file = "external_parameter_empa_cosmo14.nc"
int2lm_bin = os.path.join(input_root,"executables/int2lm")

int2lm_libgrib_dir = os.path.join(input_root, 'libgrib_api')

# COSMO
cosmo_bin = os.path.join(input_root,"executables/cosmoart") 

# Case specific settings (int2lm and cosmo namelists and runscripts)

int2lm_namelist = '%s/cases/%s/int2lm_INPUT.cfg' % (chain_src_dir,casename)
int2lm_runjob = '%s/cases/%s/int2lm_runjob.cfg' % (chain_src_dir,casename)
cosmo_namelist = '%s/cases/%s/cosmo_INPUT_' % (chain_src_dir,casename)
cosmo_runjob = '%s/cases/%s/cosmo_runjob.cfg' % (chain_src_dir,casename)


# Walltimes and domain decomposition

## INT2LM
if compute_queue=="normal":
    int2lm_walltime="01:00:00"
elif compute_queue=="debug":
    int2lm_walltime="00:30:00"
else: 
    logging.error("Unset queue name: %s" % compute_queue)
    sys.exit(1)

int2lm_nodes = 2
int2lm_ntasks_per_node = 12 
int2lm_np_x = 8
int2lm_np_y = 3
int2lm_np_tot = int2lm_np_x * int2lm_np_y

## COSMO 
if compute_queue=="normal":
    cosmo_walltime="01:00:00"
    cosmo_np_x=6
    cosmo_np_y=5
elif compute_queue=="debug":
    cosmo_walltime="00:30:00"
    cosmo_np_x=1
    cosmo_np_y=1
else:
    logging.error("Unknown queue name: %s" % compute_queue)
    sys.exit(1)

cosmo_np_io = 0
cosmo_np_tot = cosmo_np_x * cosmo_np_y + cosmo_np_io     

# Restart 
restart_step = 24

## Verification
reference_dir = os.path.join(input_root, "reference_output")

# If the output file that gets compared to the reference is not at the location
# that post_cosmo copied it to, give the path to it here. Else leave it 'None'
# output_dir = None
# Use this if the post_cosmo job is not executed
output_dir = os.environ['SCRATCH'] + "/cosmoart_processing_chain/example_cosmoart/2015020400_0_3/cosmo/output"

# variables_to_check is a dict() with a tuple() of filenames as key and a list
# of variables-names as value. The tuple consists of the filenames of the two
# files to check, the list contains the variable-names that are compared.
# The verify_chain job will look for the files in the reference_dir (first tuple
# element) and the ouput_dir (second tuple element)
values_to_check = {("reference_lffd2015020400c.nc","lffd2015020400c.nc") :
                      ['T', 'U', 'V', 'CO2_A']}
