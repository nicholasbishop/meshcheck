# meshcheck

## Purpose

Quickly-hacked together mesh viewer intended as a visual aid for
developing mesh modeling tools.

## Usage

    pip3 install --user meshcheck
    meshcheck [filename]

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

## Installation

    pip3 install --user meshcheck
    
If you see an error like this:

> error: option --single-version-externally-managed not recognized`

Then try upgrading `setuptools` and `wheel`:

    pip3 install --user --upgrade setuptools wheel
