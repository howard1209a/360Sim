import numpy as np

def _3d_polar_coord_to_cmp(polar_coord, src_resolution):
    """
    Convert polar coordinates to pixel coordinates in CMP format

    Parameters
    ----------
    polar_coord: array
        polar coord, with format [phi经度, theta纬度]
    src_resolution: list
        source resolution, with format [height, width]

    Returns
    -------
    pixel_coord: array
        the corresponding pixel coordinates in CMP format
    """

    cmp_height, cmp_width = src_resolution[0], src_resolution[1]
    u, v = np.split(polar_coord, 2, axis=-1)
    u = u.reshape(u.shape[:2])
    v = v.reshape(v.shape[:2])

    face_size_w = cmp_width // 3
    face_size_h = cmp_height // 2
    assert (face_size_w == face_size_h)  # ensure the ratio of w:h is 3:2

    x_sphere = np.round(np.cos(v) * np.cos(u), 9)
    y_sphere = np.round(np.cos(v) * np.sin(u), 9)
    z_sphere = np.round(np.sin(v), 9)

    dst_h, dst_w = np.shape(u)[:2]
    coor_x = np.zeros((dst_h, dst_w))
    coor_y = np.zeros((dst_h, dst_w))

    for i in range(6):
        if i == 0:
            temp_index1 = np.where(y_sphere < 0, 1, -1)
            temp_index2 = np.where(abs(y_sphere) >= abs(x_sphere), 1, -2)
            temp_index3 = np.where(abs(y_sphere) >= abs(z_sphere), 1, -3)
            temp_index = (temp_index1 == np.where(temp_index2 == temp_index3, 1, -2))
            u_cub = x_sphere[temp_index] / abs(y_sphere[temp_index])
            v_cub = -z_sphere[temp_index] / abs(y_sphere[temp_index])
        elif i == 1:
            temp_index1 = np.where(x_sphere > 0, 1, -1)
            temp_index2 = np.where(abs(x_sphere) >= abs(y_sphere), 1, -2)
            temp_index3 = np.where(abs(x_sphere) >= abs(z_sphere), 1, -3)
            temp_index = (temp_index1 == np.where(temp_index2 == temp_index3, 1, -2))
            u_cub = y_sphere[temp_index] / abs(x_sphere[temp_index])
            v_cub = -z_sphere[temp_index] / abs(x_sphere[temp_index])
        elif i == 2:
            temp_index1 = np.where(y_sphere > 0, 1, -1)
            temp_index2 = np.where(abs(y_sphere) >= abs(x_sphere), 1, -2)
            temp_index3 = np.where(abs(y_sphere) >= abs(z_sphere), 1, -3)
            temp_index = (temp_index1 == np.where(temp_index2 == temp_index3, 1, -2))
            u_cub = -x_sphere[temp_index] / abs(y_sphere[temp_index])
            v_cub = -z_sphere[temp_index] / abs(y_sphere[temp_index])
        elif i == 3:
            temp_index1 = np.where(z_sphere < 0, 1, -1)
            temp_index2 = np.where(abs(z_sphere) >= abs(x_sphere), 1, -2)
            temp_index3 = np.where(abs(z_sphere) >= abs(y_sphere), 1, -3)
            temp_index = (temp_index1 == np.where(temp_index2 == temp_index3, 1, -2))
            u_cub = -x_sphere[temp_index] / abs(z_sphere[temp_index])
            v_cub = -y_sphere[temp_index] / abs(z_sphere[temp_index])
        elif i == 4:
            temp_index1 = np.where(x_sphere < 0, 1, -1)
            temp_index2 = np.where(abs(x_sphere) >= abs(y_sphere), 1, -2)
            temp_index3 = np.where(abs(x_sphere) >= abs(z_sphere), 1, -3)
            temp_index = (temp_index1 == np.where(temp_index2 == temp_index3, 1, -2))
            u_cub = z_sphere[temp_index] / abs(x_sphere[temp_index])
            v_cub = -y_sphere[temp_index] / abs(x_sphere[temp_index])
        elif i == 5:
            temp_index1 = np.where(z_sphere > 0, 1, -1)
            temp_index2 = np.where(abs(z_sphere) >= abs(x_sphere), 1, -2)
            temp_index3 = np.where(abs(z_sphere) >= abs(y_sphere), 1, -3)
            temp_index = (temp_index1 == np.where(temp_index2 == temp_index3, 1, -2))
            u_cub = x_sphere[temp_index] / abs(z_sphere[temp_index])
            v_cub = -y_sphere[temp_index] / abs(z_sphere[temp_index])

        face_index = i
        m_cub = (u_cub + 1) * face_size_w / 2 - 0.5
        n_cub = (v_cub + 1) * face_size_h / 2 - 0.5
        coor_x[temp_index] = (face_index % 3) * face_size_w + m_cub
        coor_y[temp_index] = (face_index // 3) * face_size_h + n_cub

        coor_x[temp_index] = np.clip(coor_x[temp_index], (face_index % 3) * face_size_w,
                                     (face_index % 3 + 1) * face_size_w - 1)
        coor_y[temp_index] = np.clip(coor_y[temp_index], (face_index // 3) * face_size_h,
                                     (face_index // 3 + 1) * face_size_h - 1)

    pixel_coord = [coor_x, coor_y]

    return pixel_coord

print(_3d_polar_coord_to_cmp(np.array([[0, 0]]),[200,300]))