# match-courses

Cluster rows of data science course information based on course name similarity. 

Matches are calculated using Levenshtein distance.

Part of the PERVADE project.

## Installation

1. Clone this repository:

    ```
    git clone https://github.com/eddiechapman/match-courses.git
    ```

2. Enter the project directory and create a Python virtual environment:

    ```
    cd match-courses
    python3 -m venv venv
    ```

3. Activate the virtual environment and install project dependencies:

    ```
    source venv/bin/activate
    pip install .
    ```

## Usage

### `match`

```
Usage: match [OPTIONS]

  Cluster rows by course name similarity.

Options:
  --infile FILE        A CSV file containing course data
  --outfile FILE       The location where results will be stored
  --threshold INTEGER  Cutoff for determining a match between course names
  --profile            Display profiling data
  --help               Show this message and exit.

```

### `update`

```
Usage: update [OPTIONS]

  Update original course data with newly updated coding data.

Options:
  --update_data FILE  A CSV file containing updated course data
  --course_data FILE  A CSV file containing original course data
  --outfile FILE      The location where updated course data will be stored
  --help              Show this message and exit.
```