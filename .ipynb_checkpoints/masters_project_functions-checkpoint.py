########################################
#                                      #
# MASTERS PROJECT FUNCTIONS            #
#                                      #
# NABIG CHAUDHRY                       #
#                                      #
#                                      #
########################################
#####################################################################
# import packages

import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats

import lmoments3 as lm
from lmoments3 import distr as ldistr
from lmoments3 import stats as lstats

#####################################################################
# GET L-MOMENTS
# input: annual maximum series
# export: xarray dataset of l-moments

def get_lmoments(ams):
    
    ams_attributes = ams.attrs
    ams = ams.stack(allpoints=["x", "y"]).squeeze().groupby("allpoints")

    lmoments = xr.apply_ufunc(
        ldistr.gev.lmom_fit,
        ams,
        input_core_dims=[["time"]],
        exclude_dims=set(("time",)),
        output_core_dims=[[]]
    )

    lmoments = lmoments.rename("lmoments")
    new_ds = lmoments.to_dataset().to_array()

    new_ds = new_ds.unstack("allpoints")
    new_ds.attrs = ams_attributes
    new_ds.attrs["distribution"] = "gev"

    return new_ds

#####################################################################
# GET KS-STAT
# input: annual maximum series
# export: xarray dataset of ks test d-statistics and p-values

def get_ks_stat(ams):

    ams_attributes = ams.attrs
    ams = ams.stack(allpoints=["x", "y"]).squeeze().groupby("allpoints")

    def ks_stat(ams):
        
        try:
            lmoments = ldistr.gev.lmom_fit(ams)
            fitted_distr = stats.genextreme(**lmoments)
            ks = stats.kstest(
                ams,
                "genextreme",
                args=(lmoments["c"], lmoments["loc"], lmoments["scale"]),
            )
            d_statistic = ks[0]
            p_value = ks[1]
        except ValueError:
            d_statistic = np.nan
            p_value = np.nan

        return d_statistic, p_value

    d_statistic, p_value = xr.apply_ufunc(
        ks_stat,
        ams,
        input_core_dims=[["time"]],
        exclude_dims=set(("time",)),
        output_core_dims=[[], []]
    )

    d_statistic = d_statistic.rename("d_statistic")
    new_ds = d_statistic.to_dataset()
    new_ds["p_value"] = p_value

    new_ds = new_ds.unstack("allpoints")
    new_ds["d_statistic"].attrs["stat test"] = "KS test"
    new_ds["p_value"].attrs["stat test"] = "KS test"
    new_ds.attrs = ams_attributes
    new_ds.attrs["distribution"] = "gev"

    return new_ds

#####################################################################
# GET BOOTSTRAP
# input: annual maximum series and relevant parameters
# export: boostrap-calculated value for relevant parameters

def bootstrap(ams, data_variable="return_value", arg_value=10):
        
    data_variables = ["return_value", "return_prob"]
    if data_variable not in data_variables:
        raise ValueError("invalid data variable type. expected one of the following: %s" % data_variables)
    
    sample_size = len(ams)
    new_ams = np.random.choice(ams, size=sample_size, replace=True)
    
    try:
        lmoments = ldistr.gev.lmom_fit(new_ams)
        fitted_distr = stats.genextreme(**lmoments)

        if data_variable == "return_value":
            return_event = 1.0-(1./arg_value)
            return_value = fitted_distr.ppf(return_event)
            result = round(return_value, 5)

        elif data_variable == "return_prob":
            result = 1-(fitted_distr.cdf(arg_value))

    except ValueError:
        result = np.nan
    
    return result

#####################################################################
# GET RETURN VALUE
# input: annual maximum series and relevant parameters
# export: xarray dataset with return values and confidence intervals

def get_return_value(ams, return_period=10, bootstrap_runs=100,
                    conf_int_lower_bound=2.5, conf_int_upper_bound=97.5):

    ams_attributes = ams.attrs
    ams = ams.stack(allpoints=["x", "y"]).squeeze().groupby("allpoints")

    def return_value(ams):

        try:
            lmoments = ldistr.gev.lmom_fit(ams)
            fitted_distr = stats.genextreme(**lmoments)
            return_event = 1.0 - (1.0 / return_period)
            return_value = fitted_distr.ppf(return_event)
            return_value = round(return_value, 5)
        except ValueError:
            return_value = np.nan
        
        bootstrap_values = []
        data_variable = "return_value"
        for _ in range(bootstrap_runs):
            result = bootstrap(ams, data_variable="return_value",
                               arg_value=return_period)
            bootstrap_values.append(result)
        conf_int_array = np.percentile(bootstrap_values, [conf_int_lower_bound,
                                                          conf_int_upper_bound])
        conf_int_lower_limit = conf_int_array[0]
        conf_int_upper_limit = conf_int_array[1]

        return return_value, conf_int_lower_limit, conf_int_upper_limit

    
    return_value, conf_int_lower_limit, conf_int_upper_limit = xr.apply_ufunc(
                                                                return_value,
                                                                ams,
                                                                input_core_dims=[["time"]],
                                                                exclude_dims=set(("time",)),
                                                                output_core_dims=[[],[],[]]
    )

    return_value = return_value.rename("return_value")
    new_ds = return_value.to_dataset()
    new_ds["conf_int_lower_limit"] = conf_int_lower_limit
    new_ds["conf_int_upper_limit"] = conf_int_upper_limit
    
    new_ds = new_ds.unstack("allpoints")
        
    new_ds["return_value"].attrs["return period"] = "1 in {} year event".format(str(return_period))
    new_ds["conf_int_lower_limit"].attrs["confidence interval lower bound"] = "{}th percentile".format(str(conf_int_lower_bound))
    new_ds["conf_int_upper_limit"].attrs["confidence interval upper bound"] = "{}th percentile".format(str(conf_int_upper_bound))
    new_ds.attrs = ams_attributes
    new_ds.attrs["distribution"] = "gev"

    return new_ds

#####################################################################
# GET PERCENT CHANGE
# input: two xarray datasets
# export: xarray dataarray with percent change

def get_percent_change(ds_1, ds_2, data_variable='return_value'):
    
    ds_attributes = ds_1.attrs
    
    da_1 = ds_1[data_variable]
    da_2 = ds_2[data_variable]

    percent_change = (da_2-da_1)/da_1
    
    percent_change = percent_change.rename("percent_change")
    new_ds = percent_change.to_dataset()
    
    new_ds.attrs = ds_attributes
    new_ds.attrs["method"] = 'percent_change'
    
    return new_ds

#####################################################################
# GET FLAT ARRAY
# input: xarray dataset
# export: flattened numpy array

def get_flat_array(ds, data_variable='return_value', remove_nans=True):
    
    array = ds[data_variable].to_numpy()
    flat_array = array.flatten()
    
    if remove_nans:
        flat_array = flat_array[~np.isnan(flat_array)]
    
    return flat_array

#####################################################################
# GET RETURN PROBABILITY
# input: annual maximum series and relevant parameters
# export: xarray dataset with return probabilities and confidence intervals

def get_return_prob(ams, threshold, bootstrap_runs=1000,
                    conf_int_lower_bound=2.5, conf_int_upper_bound=97.5):

    ams_attributes = ams.attrs
    ams = ams.stack(allpoints=["x", "y"]).squeeze().groupby("allpoints")

    def return_prob(ams):

        try:
            lmoments = ldistr.gev.lmom_fit(ams)
            fitted_distr = stats.genextreme(**lmoments)
            return_prob = 1 - (fitted_distr.cdf(threshold))
        except ValueError:
            return_prob = np.nan
            
        bootstrap_values = []
        data_variable = "return_prob"
        for _ in range(bootstrap_runs):
            result = bootstrap(ams, data_variable="return_prob", arg_value=threshold)
            bootstrap_values.append(result)
        conf_int_array = np.percentile(bootstrap_values, [conf_int_lower_bound,
                                                          conf_int_upper_bound])
        conf_int = tuple(conf_int_array)

        return return_prob, conf_int

    return_prob, conf_int = xr.apply_ufunc(
                            return_prob,
                            ams,
                            input_core_dims=[["time"]],
                            exclude_dims=set(("time",)),
                            output_core_dims=[[],[]]
    )

    return_prob = return_prob.rename("return_prob")
    new_ds = return_prob.to_dataset()
    new_ds["conf_int"] = conf_int

    new_ds = new_ds.unstack("allpoints")

    new_ds["return_prob"].attrs["threshold"] = "exceedance of {} value event".format(
        str(threshold)
    )
    new_ds["conf_int"].attrs["confidence interval bounds"] = "({}th percentile, {}th percentile)".format(str(conf_int_lower_bound), str(conf_int_upper_bound))
    new_ds.attrs = ams_attributes
    new_ds.attrs["distribution"] = "gev"

    return new_ds

#####################################################################