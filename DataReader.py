import pandas as pd
import re

def dataReader(info=None):
  """
  Reads Gcode data from a file and returns a DataFrame with parsed values.

  Args:
      info (dict, optional): A dictionary containing file path (`filePath`) and file name (`fileName`). Defaults to None.

  Returns:
      tuple: A tuple containing two elements:
          - data (pandas.DataFrame): The DataFrame containing parsed Gcode data.
          - info (dict, optional): The input dictionary (`info`) if provided, otherwise an empty dictionary.
  """

  if info is None:
    # Case 0: Find Gcode files in the current directory
    import glob
    files = glob.glob("*.gcode")

    if len(files) > 1:
      print("Error: Too many Gcode files found!")
      return None, {}  # Return None for data and empty info

    # Create temporary file (replace with appropriate temporary file handling)
    filename = files[0]
    with open(filename, 'rb') as f_in, open('temp.dat', 'wb') as f_out:
      f_out.write(f_in.read())

  else:
    # Case 1: Use the provided file path and name
    filename = info.get('filePath', None) + '\\' + info.get('fileName', None) + ".Gcode"
    if not filename:
      print("Error: Missing file path or name in info dictionary.")
      return None, {}  # Return None for data and empty info

  # Define reading options
  opts = pd.read_csv(filename, sep=' ', header=None,
                    names=['Raw', 'Operation', 'X', 'Y', 'Z', 'Speed'],
                    dtype={'Operation': object},
                    comment=';', skipinitialspace=True, na_values=[''],
                    converters={'X': parse_float, 'Y': parse_float, 'Z': parse_float, 'Speed': parse_float})

  # Parse X, Y, Z, and Speed values (using a separate function for clarity)
  def parse_float(value):
    match = re.search(r"(?<=[\w-])\d+(\.\d+)?", value)
    return float(match.group()) if match else None

  data = opts[['X', 'Y', 'Z', 'Speed']].apply(pd.to_numeric, errors='coerce')

  # Parse Operation values and add leading 'G'
  data['Operation'] = opts['Raw'].str.extract(r"(?<=G)\d+", expand=False, sep=',').astype(str).str.cat('G', na_rep='')

  # Filter data (remove header, G92 lines, empty lines)
  data = data.loc[(data['Operation'] != 'G0') & (data['Operation'] != 'G92') & (data['Operation'] != '')]

  # Fill missing values with previous values (replace with desired interpolation method if needed)
  data = data.fillna(method='ffill')

  # Convert speed to meters per second (replace with desired unit conversion if needed)
  data['Speed'] = data['Speed'] / 60 / 1000

  # Return data and info (if provided)
  return data, info

if __name__ == "__main__":
  # Example usage (assuming you have Gcode files in the current directory)
  data, _ = dataReader()
  print(data.head())  # Print the first few rows of the DataFrame