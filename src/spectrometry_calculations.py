import numpy as np

def grating_spacing_from_lines_per_mm(lines_per_mm):
    """Calculate grating spacing in meters."""
    if lines_per_mm is None or lines_per_mm <= 0:
        return None
    return 1.0 / (lines_per_mm * 1000.0)  # d in meters

def calculate_wavelength_nm(peak_pixel_index,
                            zero_order_pixel_index,
                            L_meters,
                            d_meters,
                            pixel_scale_meters_per_pixel,
                            diffraction_order=1):
    """
    Calculates the wavelength in nanometers using the grating formula.
    d * sin(theta) = m * lambda
    theta is angle of diffraction, y is distance on sensor, L is grating-sensor distance.
    tan(theta) = y / L

    Args:
        peak_pixel_index (int): Pixel index (row) of the spectral line peak.
        zero_order_pixel_index (int): Pixel index (row) of the 0th order diffraction peak.
        L_meters (float): Distance from diffraction grating to sensor in meters.
        d_meters (float): Grating spacing in meters.
        pixel_scale_meters_per_pixel (float): Effective size of a pixel in meters.
        diffraction_order (int): The order of diffraction (m), typically 1.

    Returns:
        float: Calculated wavelength in nanometers, or None if inputs are invalid or calculation fails.
    """
    if L_meters is None or L_meters <= 0 or \
       d_meters is None or d_meters <= 0 or \
       pixel_scale_meters_per_pixel is None or pixel_scale_meters_per_pixel <= 0 or \
       peak_pixel_index is None or zero_order_pixel_index is None:
        return None

    # y is the distance on the sensor from the zero-order peak to the spectral line peak
    # The sign of y_pixels determines the sign of the angle.
    y_pixels = peak_pixel_index - zero_order_pixel_index
    y_meters = y_pixels * pixel_scale_meters_per_pixel

    # Calculate the angle theta using tan(theta) = y / L
    # np.arctan2 is robust. angle_radians will have a sign.
    angle_radians = np.arctan2(y_meters, L_meters)

    # Calculate wavelength using d * sin(theta) = m * lambda
    # So, lambda = (d * sin(theta)) / m
    if diffraction_order == 0: # Avoid division by zero for m
        return None
    
    # sin(theta) will also have a sign.
    # If y_meters is 0, angle is 0, sin(angle) is 0, wavelength is 0 (correct for 0th order).
    wavelength_meters = (d_meters * np.sin(angle_radians)) / diffraction_order
    
    # We are interested in the magnitude for display, typically for m=1 or m=-1.
    # Taking abs value here assumes user is looking at first order magnitude.
    wavelength_nm = abs(wavelength_meters * 1e9)

    return wavelength_nm