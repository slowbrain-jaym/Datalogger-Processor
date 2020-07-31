import pandas as pd
import scipy.interpolate as inter
import scipy.integrate as integrate

def heat_flux_sensor_calculation(df, sensor_information, boundary_TC):
    HeatFluxTCs = [[0.0, 0.005, 0.01, 0.015, 0.02], ['T19', 'T18', 'T20', 'T16', 'T17']]
    boundary_TC = 'T23'
    for TC in HeatFluxTCs[1]:
        df[TC+' change'] = df[TC] - df.iloc[0][TC]    
    perspex_energy = []
    for time in df.index:
        temp_interp = inter.UnivariateSpline(HeatFluxTCs[0], [df.at[time, x+' change'] for x in HeatFluxTCs[1]], s=0)
        perspex_energy.append(1190*1466*integrate.quad(temp_interp, a=0, b=0.02)[0])
    df['perspex energy'] = perspex_energy
    df['ali energy'] = df[HeatFluxTCs[1][0]+' change']*2710.0*910.0*0.002
    df['total energy'] = df['perspex energy']+df['ali energy']
    df['flux'] = df['total energy'].diff(1)/5.0
    df['HTC'] = df['flux']/(df[boundary_TC] - df[HeatFluxTCs[1][0]])
    return df

