import geopandas as gpd
import pandas as pd
import json
import gzip
import fsspec
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr


def plot_hist_map(df, var_name, var_description, color_map):

    # Create a figure with two subplots side by side
    fig, axes = plt.subplots(1, 2, figsize=(20, 10))
    
    # Plot the distribution 
    df[var_name].plot.hist(bins=30, color='gray', edgecolor='black', ax=axes[0])
    axes[0].set_title(f'Distribution of {var_description}', fontsize=18)
    axes[0].set_xlabel(f'{var_description}', fontsize=16)
    axes[0].set_ylabel('Frequency', fontsize=16)
    axes[0].grid(axis='y', alpha=0.75)
    axes[0].tick_params(axis='both', which='major', labelsize=16)
    
    # Plot the map with colors
    df.plot(column=var_name, cmap=color_map, legend=True, ax=axes[1])
    axes[1].set_title(f'Catchments Colored by {var_description}', fontsize=18)
    axes[1].tick_params(axis='both', which='major', labelsize=16)
    axes[1].set_xlabel('x projected coordinates (m)', fontsize=16)
    axes[1].set_ylabel('y projected coordinates (m)', fontsize=16)
    
    plt.tight_layout()
    plt.show()

def plot_single_cat(df, var_name, var_description, color_map, divide_id):
    # Create a figure with two subplots side by side
    fig, axes = plt.subplots(1, 2, figsize=(20, 10))
    
    # Plot the distribution 
    df[var_name].plot.hist(bins=30, color='gray', edgecolor='black', ax=axes[0])
    axes[0].set_title(f'Distribution of {var_description}', fontsize=18)
    axes[0].set_xlabel(f'{var_description}', fontsize=16)
    axes[0].set_ylabel('Frequency', fontsize=16)
    axes[0].grid(axis='y', alpha=0.75)
    axes[0].tick_params(axis='both', which='major', labelsize=16)
    
    # Plot the map with colors
    df.plot(column=var_name, cmap=color_map, legend=True, ax=axes[1])
    axes[1].set_title(f'Catchments Colored by {var_description}', fontsize=18)
    axes[1].tick_params(axis='both', which='major', labelsize=16)
    axes[1].set_xlabel('x projected coordinates (m)', fontsize=16)
    axes[1].set_ylabel('y projected coordinates (m)', fontsize=16)

    # Add the catchment of interest to the map
    df_sel = df.loc[df['divide_id']==divide_id]
    df_sel.plot(edgecolor='cyan', facecolor='none', ax=axes[1], linewidth=4)
    
    # Add a vertical line at the single value
    axes[0].axvline(df_sel[var_name].values[0], color='cyan', linestyle='dashed', linewidth=4)
    
    plt.tight_layout()
    plt.show()

def plot_selected_region(gdf_cat, gdf_flow, gdf_nexus, cat_id):
    fig, ax = plt.subplots(figsize=(7,7))
    gdf_cat.plot(ax=ax, facecolor='none', edgecolor='lightgray', zorder=1)
    gdf_cat.loc[gdf_cat['divide_id']==cat_id].plot(ax=ax, facecolor='none', edgecolor='k', linewidth=2, zorder=2)
    gdf_flow.plot(ax=ax, color='b')
    gdf_flow.loc[gdf_flow['divide_id']==cat_id].plot(color='cyan', ax=ax, linewidth=3, zorder=3)
    gdf_nexus[gdf_nexus['id']==gdf_flow.loc[gdf_flow['divide_id']==cat_id]['toid'].values[0]].plot(color='r', markersize=30, ax=ax, zorder=4)
    handles, labels = ax.get_legend_handles_labels()
    plt.show()


def nex_csv2xr(fs, csv_files):
    # Create a dictionary to hold DataFrames
    dfs = {}    
    for file in csv_files:
        file_id = file.split('/')[-1]
        df = pd.read_csv(fs.open(file), header=None)
        df['id'] = file_id.split('_')[0]
        df[1] = pd.to_datetime(df[1])
        df.rename(columns={1:'time', 2:'streamflow'}, inplace=True)
        df.drop(columns=[0], inplace=True)
        dfs[file_id] = df.set_index(['time', 'id'])

    # Concatenate all DataFrames along the 'time' and 'id' dimensions
    combined_df = pd.concat(dfs.values())

    # Convert to xarray Dataset
    xr_dataset = combined_df.to_xarray()
    return xr_dataset

def cat_csv2xr(fs, csv_files):
    # Create a dictionary to hold DataFrames
    dfs = {}
    for file in csv_files:
        file_id = file.split('/')[-1]
        df = pd.read_csv(fs.open(file))
        df['ID'] = file_id.split('.')[0]
        df['Time'] = pd.to_datetime(df['Time'])
        df.drop(columns=['Time Step'], inplace=True)
        dfs[file_id] = df.set_index(['Time', 'ID'])

    # Concatenate all DataFrames along the 'time' and 'id' dimensions
    combined_df = pd.concat(dfs.values())

    # Convert to xarray Dataset
    xr_dataset = combined_df.to_xarray()
    return xr_dataset

def forcing_csv2xr(fs, csv_files):
    # Create a dictionary to hold DataFrames
    dfs = {}
    for file in csv_files:
        file_id = file.split('/')[-1]
        df = pd.read_csv(fs.open(file))
        df = df.groupby(['time']).mean().reset_index()                 ################ update later once we make sure inputs are correct!
        df['ID'] = file_id.split('.')[0]
        df['time'] = pd.to_datetime(df['time'])
        dfs[file_id] = df.set_index(['time', 'ID'])
        
    # Concatenate all DataFrames along the 'time' and 'id' dimensions
    combined_df = pd.concat(dfs.values())
    combined_df = combined_df[~combined_df.index.duplicated(keep='first')] 
    
    # Convert to xarray Dataset
    xr_dataset = combined_df.to_xarray()
    return xr_dataset

def load_config(config_path, endpoint_url, fs):
    # Custom parser function for configuration files
    def parse_config(file_content):
        config_dict = {}
        for line in file_content.splitlines():
            if '=' in line:
                key, value = line.split('=', 1)
                config_dict[key.strip()] = value.strip()
        return config_dict
        
    try:
        # Read the configuration file
        with fs.open(config_path, 'r') as f:
            config_content = f.read()
    
        # Parse the configuration file
        config_dict = parse_config(config_content)
        return config_dict
        
        # # Pretty print the parsed configuration
        # for key, value in config_dict.items():
        #     print(f"{key}: {value}")
    except Exception as e:
        print(f"Error reading the file: {e}")


def change_config(fs, config_path, config_dict, var_name, var_value):

    # Function to convert the dictionary back to config file format
    def dict_to_config(config_dict):
        lines = []
        for key, value in config_dict.items():
            lines.append(f"{key}={value}")
        return "\n".join(lines)
        
    # Update the dictionary (e.g., change 'expon' value)
    config_dict[var_name] = var_value

    # Convert the updated dictionary back to config file format
    updated_config_content = dict_to_config(config_dict)

    # Write the updated configuration back to S3
    with fs.open(config_path, 'w') as f:
        f.write(updated_config_content)

    print("Configuration updated successfully.")


def plot_precip_and_flow(cat_sel, nex_sel, xr_cat, xr_nex, xr_forcing):

    # Create a figure and primary axis
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Get the time and streamflow values
    times = xr_nex.sel(id=nex_sel).time.values
    streamflow_data = xr_nex.sel(id=nex_sel).streamflow.values
    
    # Plot the streamflow data as a line on the primary y-axis
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Discharge (m³/s)', color='black')
    ax1.plot(times, streamflow_data, color='black', label='Discharge')
    ax1.tick_params(axis='y', labelcolor='black')
    
    # Create a secondary y-axis
    ax2 = ax1.twinx()
    ax2.set_ylabel('Precipitation (mm) per time step (hr)', color='blue')
    
    # Set the frame color to gray
    for spine in ax1.spines.values():
        spine.set_edgecolor('gray')
        spine.set_linewidth(2)
    
    for spine in ax2.spines.values():
        spine.set_edgecolor('gray')
        spine.set_linewidth(2)
    
    # Get the APCP_surface values
    apcp_surface = xr_forcing.sel(ID=cat_sel).APCP_surface.values

    # Plot the APCP_surface data as bars on the secondary y-axis
    ax2.bar(times, apcp_surface, width=0.01, color='blue', align='center', label='Precipitation')
    ax2.tick_params(axis='y', labelcolor='blue')
    
    # Invert the secondary y-axis
    ax2.invert_yaxis()
    
    # Add legend with transparent face color and located at the top right
    legend = fig.legend(loc='upper right', bbox_to_anchor=(0.9, 0.9))
    legend.get_frame().set_facecolor((1, 1, 1, 0.5))  # Set face color with transparency (white with alpha 0.5)
    
    # Adjust the layout
    ax1.grid(True, which='both', axis='both', linestyle='--', linewidth=0.5)
    # ax2.grid(True, which='both', axis='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    
    # Display the plot
    plt.show()


def plot_flow_comparison(cat_sel, nex_sel, 
                         base_forcing_xr, base_nex_xr, base_cat_xr, 
                         mod_nex_xr, mod_cat_xr):

    # Create a figure and primary axis
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Get the time and streamflow values
    times = base_nex_xr.sel(id=nex_sel).time.values
    base_streamflow_data = base_nex_xr.sel(id=nex_sel).streamflow.values
    
    # Plot the streamflow data from base simulation on the primary y-axis
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Discharge (m³/s)', color='black')
    ax1.plot(times, base_streamflow_data, color='black', linewidth=3, label='Discharge: Base Scenario')
    ax1.tick_params(axis='y', labelcolor='black')

    # Add the streamflow plot for the test simulation (modify parameters)
    mod_streamflow_data = mod_nex_xr.sel(id=nex_sel).streamflow.values
    ax1.plot(times, mod_streamflow_data, color='gray', linestyle='--', label='Discharge: Test Scenario')
    
    # Create a secondary y-axis
    ax2 = ax1.twinx()
    ax2.set_ylabel('Precipitation (mm) per time step (hr)', color='blue')
    
    # Set the frame color to gray
    for spine in ax1.spines.values():
        spine.set_edgecolor('gray')
        spine.set_linewidth(2)
    
    for spine in ax2.spines.values():
        spine.set_edgecolor('gray')
        spine.set_linewidth(2)
    
    # Get the APCP_surface values
    apcp_surface = base_forcing_xr.sel(ID=cat_sel).APCP_surface.values

    # Plot the APCP_surface data as bars on the secondary y-axis
    ax2.bar(times, apcp_surface, width=0.01, color='blue', align='center', label='Precipitation')
    ax2.tick_params(axis='y', labelcolor='blue')
    
    # Invert the secondary y-axis
    ax2.invert_yaxis()
    
    # Add legend with transparent face color and located at the top right
    legend = fig.legend(loc='upper right', bbox_to_anchor=(0.9, 0.9))
    legend.get_frame().set_facecolor((1, 1, 1, 0.5))  # Set face color with transparency (white with alpha 0.5)
    
    # Adjust the layout
    ax1.grid(True, which='both', axis='both', linestyle='--', linewidth=0.5)
    # ax2.grid(True, which='both', axis='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    
    # Display the plot
    plt.show()