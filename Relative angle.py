import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
from sklearn.neighbors import NearestNeighbors

# Read the output files generated by the first and second scripts
data_plus1 = pd.read_csv(r"C:\Users\kamil\OneDrive - Lancaster University\ANU\PHYS3042\Bubles\W_P740_NA_w_gold_repeat annealing\W_He_740C_BF_ZL_400kx_Defoc_+1mu_After_cool_crop1.csv")  # Adjust file name and path as needed
data_minus1 = pd.read_csv(r"C:\Users\kamil\OneDrive - Lancaster University\ANU\PHYS3042\Bubles\W_P740_NA_w_gold_repeat annealing\W_He_740C_BF_ZL_400kx_Defoc_-1mu_After_cool_crop.csv")  # Adjust file name and path as needed

plt.figure(figsize=(12, 10))

# Plot x and y positions of data_plus1
plt.scatter(data_plus1['x'], data_plus1['y'], label='Over-focused', color='blue')

# Plot x and y positions of data_minus1
plt.scatter(data_minus1['x'], data_minus1['y'], label='Under-focused', color='green')

plt.xlabel('x Position')
plt.ylabel('y Position')
plt.title('Initial positions')
plt.legend()
plt.grid(True)
plt.gca().invert_yaxis()

#plt.show()


def rotate(pos, angle, center):
    translated_x = pos[0] - center[0]
    translated_y = pos[1] - center[1]
    sinTheta = math.sin(angle)
    cosTheta = math.cos(angle)
    rotated_x = cosTheta * translated_x - sinTheta * translated_y
    rotated_y = sinTheta * translated_x + cosTheta * translated_y
    x = rotated_x + center[0]
    y = rotated_y + center[1]
    return [x, y]


def scale(pos, factor, center):
    translated_x = pos[0] - center[0]
    translated_y = pos[1] - center[1]
    scaled_x = translated_x * factor
    scaled_y = translated_y * factor
    x = scaled_x + center[0]
    y = scaled_y + center[1]
    return [x, y]


def transform(pos, shift, angle, factor):
    centre = [513, 497]
    shifted_pos = [pos[0] - shift[0], pos[1] - shift[1]]
    rotated_pos = rotate(shifted_pos, angle, centre)
    scaled_pos = scale(rotated_pos, factor, centre)
    return scaled_pos


transformed_positions = []
for _, row in data_minus1.iterrows():
    transformed_pos = transform([row['y'], row['x']], [-1.286, -61.45], 7.728e-4, 1.00126)
    transformed_positions.append(transformed_pos)

data_minus1_transformed = pd.DataFrame(transformed_positions, columns=['y', 'x'])
data_minus1_transformed['radius'] = data_minus1['radius']


"""
# Optimization
#row +-1 need to be (,2) shape
data_plus1_no_rad = data_plus1.drop(columns=['radius'])


# Define objective function to minimize distance between corresponding points
def objective(params, data_plus1_no_rad, data_minus1_transformed):
    shift_y, shift_x, angle, factor = params
    
    # Apply transformation to data_minus1_transformed
    transformed_positions = []
    for _, row in data_minus1_transformed.iterrows():
        transformed_pos = transform([row['y'], row['x']], [shift_y, shift_x], angle, factor)
        transformed_positions.append(transformed_pos)
    
    # Calculate total distance between corresponding points
    total_distance = 0
    for i, row_plus1 in data_plus1_no_rad.iterrows():
        min_distance = 60
        for j, row_minus1 in enumerate(transformed_positions):
            distance = np.linalg.norm(np.array(row_plus1) - np.array(row_minus1))
            if distance < min_distance:
                min_distance = distance
        total_distance += min_distance
    
    return total_distance

# Initial guess for optimization
initial_guess = [-10, -70, -0.05, 1.05]

# Define bounds for parameters
bounds = [(-100, 100), (-100, 100), (-np.pi/4, np.pi/4), (0.9, 1.1)]
# Define the callback function to print the progress
def callback(xk, convergence):
    print("Iteration:", len(xk), "Best Objective Value:", convergence)

# Perform optimization with callback
result = differential_evolution(objective, bounds, args=(data_plus1_no_rad, data_minus1_transformed) ,callback=callback)



# Get optimized parameters
shift_y, shift_x, angle, factor = result.x

print(result)

"""



scale_factor = 1.00126
angle = 7.728e-4
translation = [-61.5, -1.3]

plt.figure(figsize=(12, 10))

# Plot the transformed positions of both datasets
plt.scatter(data_plus1['x'], data_plus1['y'], label='Over-focused (original)', color='blue')
plt.scatter(data_minus1_transformed['x'], data_minus1_transformed['y'], label='Under-focused (transformed)', color='green')

params_text = f"Shift: {translation}\nScaling: {scale_factor:.4f}\nRotation: {angle*180/np.pi:.3f}°"
plt.text(0.05, 0.3, params_text, transform=plt.gca().transAxes, fontsize=20, verticalalignment='top', bbox=dict(boxstyle="round,pad=0.3", edgecolor='gray', facecolor='white'))

plt.xlabel('x Position',fontsize = 20)
plt.ylabel('y Position',fontsize = 20)
plt.title('Under-focused points mapped onto the over-focused points', fontsize = 20)
plt.legend(fontsize = 20)
plt.grid(True)

plt.gca().invert_yaxis()

plt.xticks(fontsize=20)
plt.yticks(fontsize=20)

#plt.show()

# Add columns for bubble and tested for both datasets
data_plus1['bubble'] = 0  # Initialize bubble column for over-focused image
data_plus1['tested'] = -1  # Initialize tested column for over-focused image

data_minus1_transformed['bubble'] = 0  # Initialize bubble column for under-focused image
data_minus1_transformed['tested'] = -1  # Initialize tested column for under-focused image

# CHANGE PARAMETERS HERE
# Manually select an initial bubble for both datasets
initial_bubble_index_plus1 = 93#93#52 #93
initial_bubble_index_minus1 = 11#(top right point) #117#74 #117 
radius = 40  # Radius for nearest neighbors; adjust radius as needed
angle_threshold = 2  # Threshold for angle comparison
distance_threshold = 10  # Distance threshold for selecting neighbors

# Define function to calculate angle between three points
def calculate_angle(p1, p2, p3):
    v1 = p1 - p2
    v2 = p3 - p2
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    if norm_v1 == 0 or norm_v2 == 0:
        return np.nan  # Return NaN if one of the vectors is zero
    dot_product = np.dot(v1, v2) / (norm_v1 * norm_v2)
    dot_product = np.clip(dot_product, -1.0, 1.0)  # Clip the value to be in the valid range for arccos
    angle_rad = np.arccos(dot_product)
    angle_deg = np.degrees(angle_rad)
    return angle_deg

# Define function to check if a blob is a bubble based on angle comparison
def is_bubble(blob_plus1, blob_minus1, reference_plus1, reference_minus1):
    pos_plus1 = np.array([blob_plus1['y'], blob_plus1['x']])
    pos_minus1 = np.array([blob_minus1['y'], blob_minus1['x']])
    ref_plus1 = np.array([reference_plus1['y'], reference_plus1['x']])
    ref_minus1 = np.array([reference_minus1['y'], reference_minus1['x']])
    
    angle1 = calculate_angle(pos_plus1, ref_plus1, pos_minus1)
    angle2 = calculate_angle(pos_minus1, ref_minus1, pos_plus1)
    
    if np.isnan(angle1) or np.isnan(angle2):
        return False  # If any angle is NaN, it's not a bubble
    
    return abs(angle1 - angle2) <= angle_threshold

# Build spatial index for the dataset
def build_spatial_index(data):
    X = data[['y', 'x']].values  # Extract x and y coordinates
    nn_index = NearestNeighbors(radius=radius).fit(X)
    return nn_index

# Find neighboring blobs within the radius for a given blob
def find_neighbors(blob, nn_index, data):
    X = data[['y', 'x']].values  # Extract x and y coordinates of all blobs
    query_point = [[blob['y'], blob['x']]]  # Convert blob to a query point
    neighbors_indices = nn_index.radius_neighbors(query_point, return_distance=False)[0]
    neighbors = [data.iloc[i] for i in neighbors_indices]
    return neighbors

# Build spatial index for data_plus1
nn_index_plus1 = build_spatial_index(data_plus1)

# Build spatial index for data_minus1
nn_index_minus1 = build_spatial_index(data_minus1_transformed)

# Reference points
reference_plus1 = data_plus1.iloc[initial_bubble_index_plus1]
reference_minus1 = data_minus1_transformed.iloc[initial_bubble_index_minus1]

# Iterate through each bubble in the over-focused dataset
for index_plus1, bubble_plus1 in data_plus1.iterrows():
    # Find nearest neighbors in both datasets
    neighbors_plus1 = find_neighbors(bubble_plus1, nn_index_plus1, data_plus1)
    neighbors_minus1 = find_neighbors(bubble_plus1, nn_index_minus1, data_minus1_transformed)
    
    # Check angles between each pair of neighbors
    for neighbor_plus1 in neighbors_plus1:
        for neighbor_minus1 in neighbors_minus1:
            if np.linalg.norm(np.array([neighbor_plus1['y'], neighbor_plus1['x']]) - np.array([neighbor_minus1['y'], neighbor_minus1['x']])) <= distance_threshold:
                if is_bubble(neighbor_plus1, neighbor_minus1, reference_plus1, reference_minus1):
                    data_plus1.at[neighbor_plus1.name, 'bubble'] = 1
                    data_minus1_transformed.at[neighbor_minus1.name, 'bubble'] = 1

# Plot results

plt.figure(figsize=(12, 10))
# Plot the detected bubbles
print("Number of rows in data_plus1:", data_plus1.shape[1])
print("Number of rows in data_minus1_transformed:", data_minus1_transformed.shape[0])
print(data_minus1_transformed.iloc[74])
print(data_plus1.iloc[52])
print(data_plus1)

bubbles_plus1 = data_plus1[data_plus1['bubble'] == 1]
bubbles_minus1_transformed = data_minus1_transformed[data_minus1_transformed['bubble'] == 1]
highlight_points = np.array([[data_plus1.iloc[initial_bubble_index_plus1]['x'], data_plus1.iloc[initial_bubble_index_plus1]['y']], 
                             [data_minus1_transformed.iloc[initial_bubble_index_minus1]['x'],data_minus1_transformed.iloc[initial_bubble_index_minus1]['y']]])
highlight_points2 = np.array([[472, 426], [491, 426], [479, 443]])


plt.scatter(data_plus1['x'],data_plus1['y'], s=data_plus1['radius']*100, color='lightblue', alpha=0.7, label='+1 original')
plt.scatter(data_minus1_transformed['x'], data_minus1_transformed['y'], s=data_minus1_transformed['radius']*100, color='lightgreen', alpha=0.7, label='-1 transformed')
plt.scatter(bubbles_plus1['x'], bubbles_plus1['y'], s=bubbles_plus1['radius']*100, label='+1 filtered', color='blue')
plt.scatter(bubbles_minus1_transformed['x'], bubbles_minus1_transformed['y'], s=bubbles_minus1_transformed['radius']*100, label='-1 transformed filtered', color='green')

for i, point in enumerate(highlight_points):
    if i == 0:
        plt.scatter(point[0], point[1], s=300, color='red', edgecolors='black', marker='d', alpha=0.3, label='Reference point')
    else:
        plt.scatter(point[0], point[1], s=300, color='red', edgecolors='black', marker='d', alpha=0.3)
for i, point in enumerate(highlight_points2):
    if i == 0:
        plt.scatter(point[0], point[1], s=300, color='yellow', edgecolors='black', marker='D', alpha=0.5, label='Points of Interest')
    else:
        plt.scatter(point[0], point[1], s=300, color='yellow', edgecolors='black', marker='D', alpha=0.5)



plt.xlabel('x Position', fontsize = 35)
plt.ylabel('y Position', fontsize = 35)
plt.title('Bubble Positions and Radii\nR: {} pixels $\phi$: {}degrees N(+1/-1): {}&{} $\delta$: {}'.format(radius, angle_threshold,initial_bubble_index_plus1,initial_bubble_index_minus1,distance_threshold),fontsize = 30)
plt.legend(fontsize = 15)
plt.grid(True)

plt.gca().invert_yaxis()
plt.xticks(fontsize = 35)
plt.yticks(fontsize = 35)
#plt.gca().set_aspect('equal', adjustable='box')  # Set aspect ratio to equal
#plt.savefig(r'C:\Users\kamil\OneDrive - Lancaster University\ANU\PHYS3042\Bubles\Useful files\Angular results\rad{}ang{}dist{}ref+{},-{}.png'.format(radius, angle_threshold,distance_threshold,initial_bubble_index_plus1,initial_bubble_index_minus1))


plt.show()


# Save updated data to new output files for both datasets
bubble_plus1.to_csv(r'C:\Users\kamil\OneDrive - Lancaster University\ANU\PHYS3042\Bubles\Useful files\Angular results\angAC+1bubblesbig_rad{}.csv'.format(radius), index=True)  # Adjust file name and path as needed
bubbles_minus1_transformed.to_csv(r'C:\Users\kamil\OneDrive - Lancaster University\ANU\PHYS3042\Bubles\Useful files\Angular results\angAC-1bubblesbig_rad{}.csv'.format(radius), index=True)  # Adjust file name and path as needed
#data_minus1_transformed.to_csv(r'C:\Users\kamil\OneDrive - Lancaster University\ANU\PHYS3042\Bubles\Useful files\After Cool\Ang-1_mapped_points.csv', index = False)



fig, ax = plt.subplots(figsize=(12, 10))  

fig.patch.set_alpha(0)
ax.patch.set_alpha(0)

# Plot the data
ax.scatter(data_plus1['x'],data_plus1['y'], s=data_plus1['radius']*100, color='lightblue', alpha=0, label='Over-focused (original)')
ax.scatter(data_minus1_transformed['x'], data_minus1_transformed['y'], s=data_minus1_transformed['radius']*100, color='lightgreen', alpha=0, label='Under-focused transformed (original)')
ax.scatter(bubbles_plus1['x'], bubbles_plus1['y'], s=bubble_plus1['radius']*100, color='blue', label='Over-focused bubbles')
ax.scatter(bubbles_minus1_transformed['x'], bubbles_minus1_transformed['y'], s=bubbles_minus1_transformed['radius']*100, color='green', label='Under-focused bubbles')
           
for i, point in enumerate(highlight_points):
    if i == 0:
        plt.scatter(point[0], point[1], s=100, color='red', edgecolors='black', marker='o', alpha=0.3, label='Reference point')
    else:
        plt.scatter(point[0], point[1], s=100, color='red', edgecolors='black', marker='o', alpha=0.3)
for i, point in enumerate(highlight_points2):
    if i == 0:
        plt.scatter(point[0], point[1], s=200, color='yellow', edgecolors='black', marker='o', alpha=0.5, label='Points of Interest')
    else:
        plt.scatter(point[0], point[1], s=200, color='yellow', edgecolors='black', marker='o', alpha=0.5)


# Invert x-axis if necessary
ax.invert_yaxis()

# Remove axes
ax.axis('off')

plt.savefig(r'C:\Users\kamil\OneDrive - Lancaster University\ANU\PHYS3042\Bubles\Useful files\Angular results\trans_rad{}ang{}dist{}ref+{},-{}.png'.format(radius, angle_threshold,distance_threshold,initial_bubble_index_plus1,initial_bubble_index_minus1, transparent=True, dpi=300))


plt.show()