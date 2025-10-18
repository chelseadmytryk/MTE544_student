from math import atan2, asin, sqrt
import ast
from array import array
import csv, json, math, re

M_PI=3.1415926535
_FLOAT_RE = re.compile(r"[-+]?(?:inf|nan|(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)",
                       re.IGNORECASE)
class Logger:
    def __init__(self, filename, headers=["e", "e_dot", "e_int", "stamp"]):
        self.filename = filename

        with open(self.filename, 'w') as file:
            header_str=""

            for header in headers:
                header_str+=header
                header_str+=", "
            
            header_str+="\n"
            
            file.write(header_str)


    def log_values(self, values_list):
        with open(self.filename, 'a') as file:
            vals_str=""

            # TODO Part 5: Write the values from the list to the file
            for val in values_list:
                vals_str+=str(val)
                vals_str+=", "
            vals_str+="\n"
            file.write(vals_str)
            

    def save_log(self):
        pass

class FileReader:
    def __init__(self, filename, delimiter=","):
        self.filename = filename
        self.delimiter = delimiter

    def read_file_1(self):
        with open(self.filename, "r", newline="") as f:
            rows = list(csv.reader(f, delimiter=self.delimiter))
        if not rows:
            return [], []

        headers = rows[0]
        table = []
        for r in rows[1:]:
            row = []
            for c in r:
                s = c.strip()
                if not s:
                    continue
                # Only treat bracketed cells as JSON (used by Laser ranges)
                if s.startswith("[") and s.endswith("]"):
                    try:
                        row.append(json.loads(s))  # -> list with None where inf/NaN were
                        continue
                    except Exception:
                        pass
                # Everything else: try float; if it fails, keep as string
                try:
                    row.append(float(s))
                except ValueError:
                    row.append(s)
            if row:
                table.append(row)
        return headers, table


    def _parse_bracket_list(s: str):
        """Parse '[ ... ]' into list; supports 'inf/-inf/nan' and JSON lists."""
        s = s.strip()
        if not (s.startswith("[") and s.endswith("]")):
            return None
        # Try JSON first (works if you saved None instead of inf/nan)
        try:
            return json.loads(s)
        except Exception:
            pass
        # Fallback: regex-parse tokens
        out = []
        for tok in _FLOAT_RE.findall(s[1:-1]):
            t = tok.lower()
            if t in ("inf", "+inf"):      out.append(math.inf)
            elif t == "-inf":             out.append(-math.inf)
            elif t in ("nan","+nan","-nan"): out.append(math.nan)
            else:                         out.append(float(tok))
        return out

    def read_file(self):
        headers, table = [], []
        with open(self.filename, "r", newline="") as f:
            reader = csv.reader(f)

            # headers
            try:
                headers = [h.strip() for h in next(reader)]
                headers = [h for h in headers if h]  # drop trailing empty from a final comma
            except StopIteration:
                return [], []

            # rows
            for cells in reader:
                if not cells:
                    continue
                row = []
                for c in cells:
                    s = (c or "").strip()
                    if not s:
                        continue
                    # Laser ranges saved as one bracketed cell
                    if s.startswith("[") and s.endswith("]"):
                        row.append(_parse_bracket_list(s))
                        continue
                    # scalars
                    ls = s.lower()
                    if ls in ("inf", "+inf"):          row.append(math.inf);  continue
                    if ls == "-inf":                   row.append(-math.inf); continue
                    if ls in ("nan","+nan","-nan"):    row.append(math.nan);  continue
                    if ls == "null":                   row.append(None);      continue
                    try:
                        row.append(float(s))
                    except ValueError:
                        row.append(s)
                if row:
                    table.append(row)
        return headers, table



# TODO Part 5: Implement the conversion from Quaternion to Euler Angles
def euler_from_quaternion(x, y, z, w):
    """
    Convert quaternion (w in last place) to euler roll, pitch, yaw.
    quat = [x, y, z, w]
    """
    # just unpack yaw because yaw is z, which is the only thing we are tracking
    # x, y, z, w = quat
    # siny_cosp = 2.0 * (w * z + x * y)
    # cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    # yaw = atan2(siny_cosp, cosy_cosp)
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    yaw = atan2(siny_cosp, cosy_cosp)

    return yaw # in radians


def _coerce_cell(cell):
    s = cell.strip()
    # common fast paths
    if s.lower() in ("nan", "inf", "+inf", "-inf"):
        try:
            return float(s)
        except Exception:
            return s
    # try float
    try:
        return float(s)
    except Exception:
        pass
    # try literal (handles "[...]" and "array('f', [...])")
    try:
        obj = ast.literal_eval(s)
        if isinstance(obj, array):
            return list(obj)
        return obj
    except Exception:
        return s  # leave as raw string