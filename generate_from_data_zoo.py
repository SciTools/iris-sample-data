import glob
import os
import shutil

import iris
import iris.analysis
import iris.coord_categorisation as iris_cat


DATA_ZOO = '/data/local/dataZoo'


def global_map(target_dir):
    fname = os.path.join(DATA_ZOO, 'PP', 'aPPglob1', 'global.pp')
    target = os.path.join(target_dir, 'air_temp.pp')
    shutil.copy(fname, target)

    
def custom_file_loading(target_dir):
    fname = os.path.join(DATA_ZOO, 'ascii', 'NAME', '20100509_18Z_variablesource_12Z_VAAC', 'Fields_grid1_201005110600.txt')
    shutil.copy(fname, target_dir)

    
def hovmoller(target_dir):
    fname = os.path.join(DATA_ZOO, 'PP', 'ostia', 'ostia_sst_200604_201009_N216.pp')
    cube = iris.load_cube(fname, iris.Constraint('surface_temperature', latitude=lambda v: -5 < v < 5))
    
    iris_cat.add_month_number(cube, cube.coord('time'), 'month')
    iris_cat.add_year(cube, cube.coord('time'), 'year')
    
    monthly_mean = cube.aggregated_by(['year', 'month'], iris.analysis.MEAN)
    monthly_mean.remove_coord('month')
    monthly_mean.remove_coord('year')
    
    # make time the dimension coordinate (wont be needed once Bill has #22)
    t = monthly_mean.coord('time')
    monthly_mean.remove_coord(t)
    monthly_mean.add_dim_coord(t, 0)
    
    iris.save(monthly_mean, os.path.join(target_dir, 'ostia_monthly.nc'))

    
def rotated_pole(target_dir):
    fname = os.path.join(DATA_ZOO, 'PP', 'aPProt1', 'rotated.pp')
    cube = iris.load_cube(fname)
    # XXX consider taking a 20x20 window for meaning 
    cube = cube[::20, ::20]
    iris.save(cube, os.path.join(target_dir, 'rotated_pole.nc'))

    
def deriving_phenomena(target_dir):
    fname = os.path.join(DATA_ZOO, 'PP', 'COLPEX', 'air_potential_and_air_pressure.pp')
    out = open(os.path.join(target_dir, 'colpex.pp'), 'wb')
    for field in iris.fileformats.pp.load(fname):
        # reduce the spatial data by a factor of 20 (5x5).
        field.data = field.data[::5, ::5]
        field.lbnpt = field.data.shape[0]
        field.lbrow = field.data.shape[1]
        field.x = field.x[::5]
        field.x_lower_bound = field.x_lower_bound[::5]
        field.x_upper_bound = field.x_upper_bound[::5]
        field.y = field.y[::5]
        field.y_lower_bound = field.y_lower_bound[::5]
        field.y_upper_bound = field.y_upper_bound[::5]
        field.save(out)

                
def cross_section(target_dir):
    fname = os.path.join(DATA_ZOO, 'PP', 'COLPEX', 'theta_and_orog_subset.pp')
    cube = iris.load_cube(fname, 'air_potential_temperature')
    cube = cube[0, :15, ...]
    iris.save(cube, os.path.join(target_dir, 'hybrid_height.nc'))


def TEC(target_dir):
    fname = os.path.join(DATA_ZOO, 'NetCDF', 'space_weather', 'Test.nc')
    target = os.path.join(target_dir, 'space_weather.nc')
    shutil.copy(fname, target)


def COP_maps(target_dir):
    for scenario in ['E1', 'A1B']:
        fname = os.path.join(DATA_ZOO, 'PP', 'A1B-Image_E1', scenario, 
                             '000100000000.01.03.236.000128.2098.12.01.00.00.pp'
                             )
                             
        target = os.path.join(target_dir, '%s.2098.pp' % scenario)
        shutil.copy(fname, target)
        
    # get the global industrial average temps:
    fname = os.path.join(DATA_ZOO, 'PP', 'A1B-Image_E1', 'pp_1859_1889_avg.pp')
    target = os.path.join(target_dir, 'pre-industrial.pp')
    shutil.copy(fname, target)
    

def COP_1d(target_dir):
    for scenario in ['E1', 'A1B']:
        fname = os.path.join(DATA_ZOO, 'PP', 'A1B-Image_E1', scenario, 
                             '*.pp'
                             )
        cube = iris.load_cube(fname)
        cube = cube.extract(iris.Constraint(longitude=lambda v: 225 <= v <= 315,
                                           latitude=lambda v: 15 <= v <= 60,
                                           )
                           )
        cube.attributes['Model scenario'] = scenario
        iris.save(cube, os.path.join(target_dir, '%s_north_america.nc' % scenario))


def lagged_ensemble(target_dir):
    fname_template = os.path.join(DATA_ZOO, 'PP', 'GloSea4', 'prodf*_')
    target_dir = os.path.join(target_dir, 'GloSea4')
    if not os.path.exists(target_dir):
        os.makedirs(os.path.join(target_dir, 'GloSea4'))
    
    
    for ensemble_num in range(14):
        ensemble_num = '%03i' % ensemble_num
        fnames = glob.glob(fname_template + ensemble_num + '.pp')
        # handle the missing ensemble
        if fnames:
            out = open(os.path.join(target_dir, 'ensemble_%s.pp' % ensemble_num), 'wb')
            fname, = fnames
            for field in iris.fileformats.pp.load(fname):
                if field.stash == 'm01s00i024':
                    field.save(out)


def custom_file_loading(target_dir):
    fname = os.path.join(DATA_ZOO, 'ascii', 'NAME', 'Eyjafjallajokull', 'Fields_grid88_201005110600.txt')
    target = os.path.join(target_dir, 'NAME_output.txt')
    shutil.copy(fname, target)


def ukV2_in_userguide(target_dir):
    fname = os.path.join(DATA_ZOO, 'PP', 'ukV2', 'THOxayrk.pp')
    sa = 'm01s00i033'
    ap = 'm01s00i004'
    pt, sa = iris.load_cube(fname, ['air_potential_temperature', 'surface_altitude'])
    # extract, via indices, an area over the north of England
    pt, sa = [cube[..., 290:494, 190:377] for cube in [pt, sa]]
    # remove the temporal dimension of the surface altitude
    sa = sa[0, ...]
    # reduce the height to the first 21 levels (every third)
    pt = pt[:, :21:3, ...]
    cubes = [pt, sa]
    iris.save(cubes, os.path.join(target_dir, 'uk_hires.pp'))
    
    
if __name__ == '__main__':
    target_dir = os.path.join(os.path.dirname(__file__), 'sample_data')
    
    open(os.path.join(target_dir, 'version.txt'), 'w').write('1.0')

    global_map(target_dir)
    custom_file_loading(target_dir)
    hovmoller(target_dir)
    rotated_pole(target_dir)
    deriving_phenomena(target_dir)
    TEC(target_dir)
    cross_section(target_dir)
    COP_maps(target_dir)
    COP_1d(target_dir)
    lagged_ensemble(target_dir)
    custom_file_loading(target_dir)
    ukV2_in_userguide(target_dir)
