import csv
import pathlib
import re

import click
from thefuzz import fuzz

BAD_PUNCT = [".", ":", "/", "-", "&", ","]
STOPWORDS = [
    "of", "in" "for", "to", "i", "ii", "iii", "iv", 
    "v", "introduction", "advanced", "or", "the"
]


def clean(string):
    for token in STOPWORDS:
        pattern = r"\b" + re.escape(token) + r"\b"
        string = re.sub(pattern, "", string)
    
    for character in BAD_PUNCT:
        string = string.replace(character, "")

    string = string.replace("  ", " ")
    string = string.strip()

    return string


@click.command()
@click.option(
    "--infile", 
    type=click.Path(
        exists=True, 
        dir_okay=False, 
        path_type=pathlib.Path
    ), 
    help="A CSV file containing course data"
)
@click.option(
    "--outfile", 
    type=click.Path(
        dir_okay=False, 
        writable=True, 
        path_type=pathlib.Path
    ), 
    default=pathlib.Path.cwd() / "matches.csv", 
    help="The location where results will be stored"
)
@click.option(
    "--threshold", 
    default=95,
    help="Cutoff for determining a match between course names"
)
@click.option(
    "--profile", 
    is_flag=True,
    help="Display profiling data"
)
def match(infile, outfile, threshold, profile):
    """
    Match course names by similarity. 
    """
    if profile:
        import cProfile
        import pstats
        import io
        import atexit

        click.echo("Profiling...")
        profiler = cProfile.Profile()
        profiler.enable()

        def exit():
            profiler.disable()
            click.echo("Profiling completed")
            with io.StringIO() as s:
                stats = pstats.Stats(profiler, stream=s)
                stats.sort_stats("cumulative")
                stats.print_stats()
                print(s.getvalue())

        atexit.register(exit)

    click.echo(f"Reading course data from " + click.style(infile.resolve(), fg="blue"))

    courses = {}
    matches = {}

    with infile.open('r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            course_id = row["course id"]
            row["clean name"] = clean(row["course"])
            courses[course_id] = row
            matches[course_id] = set()

    click.echo("Matching course names...")

    with click.progressbar(courses.items()) as bar:
        for course_id, course in bar:
            for other_id, other_course in courses.items():
                if course_id == other_id:
                    continue
                similarity = fuzz.ratio(course["clean name"], other_course["clean name"])
                if similarity >= threshold:
                    matches[course_id].add(other_id)

    click.echo("Combining secondary matches...")

    for course_id in list(matches):
        if not course_id in matches:
            continue
        secondary_matches = set()
        for match_id in list(matches[course_id]):
            try:
                secondary_matches.update(matches.pop(match_id))
            except KeyError:
                continue
            else:
                secondary_matches.discard(course_id)
        matches[course_id].update(secondary_matches)

    click.echo("Writing results to file...")

    with outfile.open('w') as f:
        fieldnames = ["course id", "degree level", "degree category", "course", "code", "code2"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for course_id, match_ids in matches.items():
            course = {k: v for k, v in courses[course_id].items() if k in fieldnames}
            writer.writerow(course)
            for match_id in match_ids:
                match = {k: v for k, v in courses[match_id].items() if k in fieldnames}
                writer.writerow(match)

    click.echo(f"Success. Results have been written to " + click.style(outfile.resolve(), fg="blue"))


@click.command()
@click.option(
    "--update_data", 
    type=click.Path(
        exists=True, 
        dir_okay=False, 
        path_type=pathlib.Path
    ), 
    help="A CSV file containing updated course data"
)
@click.option(
    "--course_data", 
    type=click.Path(
        exists=True, 
        dir_okay=False, 
        path_type=pathlib.Path
    ), 
    help="A CSV file containing original course data"
)
@click.option(
    "--outfile", 
    type=click.Path(
        dir_okay=False, 
        writable=True, 
        path_type=pathlib.Path
    ), 
    default=pathlib.Path.cwd() / "courses_updated.csv", 
    help="The location where updated course data will be stored"
)
@click.option(
    "--coder", 
    help="The person who will be attributed for any updated rows"
)
def update(update_data, course_data, outfile, coder):
    """
    Update original course data with newly updated coding data.
    """
    click.echo("Reading update data from " + click.style(update_data.resolve(), fg="blue"))
    
    updates = {}
    with update_data.open('r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            course_id = row["course id"]
            updates[course_id] = row

    click.echo("Reading course data from " + click.style(course_data.resolve(), fg="blue"))
    
    courses = {}
    with course_data.open('r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            course_id = row["course id"]
            courses[course_id] = row

    click.echo("Updating course data...")
    
    rows = []
    for course_id, original in courses.items():
        try:
            update = updates[course_id]
        except KeyError:
            pass
        else:
            if original["code"] != update["code"] or original["code2"] != update["code2"]:
                original["code"] = update["code"]
                original["code2"] = update["code2"]
                original["assigned to"] = coder
        finally:
            rows.append(original)

    click.echo("Writing results to file...")

    with outfile.open("w") as f:
        fieldnames = rows[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    click.echo(f"Success. Results have been written to " + click.style(outfile.resolve(), fg="blue"))