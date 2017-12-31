# meshcheck

## Purpose

Quickly-hacked together mesh viewer intended as a visual aid for
developing mesh modeling tools.

## Usage

    pipenv run python -m meshcheck [filename]

Input can be passed in either as a file path or via stdin.

LMB rotates the view.

## Input Format

The input is a simple JSON format that lists vertices and faces. Each
vertex gets a string label followed by its coordinates, and faces
refer to vertices by their labels.

Example:

    {
      "verts" : {
      "foo" : [0, 0, 0],
      "bar" : [1, 0, 0],
      "baz" : [0, 1, 0]
      },

      "faces" : {
      "blah" : ["foo", "bar", "baz"]
      }
    }

Two additional example files are included in the repo.
