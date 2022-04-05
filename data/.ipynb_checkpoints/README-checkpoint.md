# placeholder readme file
# add information about where data was obtained

!pip install dask-cloudprovider==2021.9.0
from dask.distributed import Client
from dask_cloudprovider.aws import FargateCluster
cluster = FargateCluster(n_workers=100, image='pangeo/pangeo-notebook:2021.10.19',
                         environment=env, scheduler_timeout='10 minutes')
client = Client(cluster)
print(cluster.dashboard_link)

os.environ['AWS_DEFAULT_REGION'] = 'us-west-1'
env = {k: os.environ[k] for k in ('AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY')}

cat = intake.open_catalog('s3://cdcat/cae.yaml')
print(list(cat))

ds = cat['file_name_from_cat_list'].to_dask()
da = ds['T2']

ams = da.resample(time="A").max(keep_attrs=True)
ams = ams.compute()
ams.to_netcdf('./data/processed/9km/file_name_from_cat_list.nc')