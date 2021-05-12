import config, pieces

def applyMatrixTransform(position, matrix, bounds = None):
    output = []
    for i in range(len(matrix)):
        x_pos = matrix[i][0] + position[0]
        y_pos = matrix[i][1] + position[1]
        if bounds == None or (bounds[0] <= x_pos <= bounds[1] and bounds[2] <= y_pos <= bounds[3]):
            output.append((x_pos, y_pos))

    return output

def getTileFromPosition(position):
    x_tile = position[0] // config.window["tile_size"]
    y_tile = 7 - position[1] // config.window["tile_size"]

    return (x_tile, y_tile)