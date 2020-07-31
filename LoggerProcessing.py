import pandas as pd
import scipy.interpolate as inter
import numpy as np
import scipy.signal as sig

def mintime(time):
    return 5*np.ceil(time/5.0)

def maxtime(time):
    return 5*np.floor(time/5.0)

def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = sig.butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data):
    """Butterworth low pass filter to remove noise from electrical components in the oven"""
    order = 5
    fs = 10.0   # sample rate, Hz
    cutoff = 0.025# desired cutoff frequency of the filter, Hz
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = sig.filtfilt(b, a, data)
    return y

def partial_derivative2d(function, x, y, dx, dy):
    value1 = function(x-dx/2, y-dy/2)
    value2 = function(x+dx/2, y+dy/2)
    return (value2-value1)/np.sqrt(dx**2+dy**2)
    
def CloughTocher2d_interpolator(xref, yref, vals):
    """ 2d interpolation (requires Scipy).
     
    This is a convenience wrapper around
    scipy.interpolation.CloughTocher2Dinterpolator, that saves you
    having to worry about using meshgrid.
 
    Parameters
    ----------
    xref, yref : array of floats, shapes (J,), (I,)
      Reference coordinate grid. The grid must be equally spaced along
      each direction, but the spacing can be different between
      directions.
    vals : array of floats, shape (I, J)
      Reference values at the reference grid positions.
 
    Returns
    -------
    interpolator: CloughTocher2DInterpolater instance
      Object that accepts a (y,x) tuple (note reversed order from the
      input to this function!) and returns the interpolated value.
 
    See Also
    --------
    barak.plot.arrplot for plotting the reference and interpolated arrays.
    """
 
    assert (len(yref), len(xref)) == vals.shape
    XREF,YREF = np.meshgrid(xref, yref)
    
    interpolator = inter.CloughTocher2DInterpolator((XREF.ravel(), YREF.ravel()),
                                              vals.ravel())
 
    return interpolator
    

def interpolate_and_filter(df, columns):
    """Interpolates and filters dataframe temperature values, returns the "RAW" 
    interpolated values and low pass filtered values"""
    #columns = ['T0']
    time_columns = [col+" time" for col in columns]
    min_time = mintime(df[time_columns].min().max())
    max_time = maxtime(df[time_columns].max().min())
    print('LOGGER  ',min_time, max_time)
    time_series = np.arange(min_time, max_time, 5)
    filter_time_series = np.arange(min_time, max_time, 1/10)
    df_pt = {}
    df_pt['time'] = time_series
    for column in columns:
        df_col = df[[column, column+" time"]].dropna()
        df_col.sort_values(by=column+" time", inplace=True)
        df_col[column].iloc[0] = df_col[column].iloc[1]
        #print df_col[column]
        s = inter.interp1d(df_col[column+" time"], df_col[column])
        df_pt[column+'RAW'] = s(time_series)
        filter_T = butter_lowpass_filter(s(filter_time_series))
        s = inter.interp1d(filter_time_series, filter_T)
        df_pt[column] = s(time_series)
        #df_pt[column+'d/dt'] = s.derivative(1)(time_series)
    df_pt = pd.DataFrame(df_pt, index=df_pt['time'])
    df_pt = df_pt.drop('time',1)
    return df

files_to_process = []
columns_to_include = ['T19', 'T18', 'T20', 'T16', 'T17','T23','T21','T22','T24','T25','T26','T27','T28']

for files in files_to_process:
    df = pd.read_csv(files+".csv")
    df = interpolate_and_filter(df, columns_to_include)
    df.write_feather(files+"processed.feather")   