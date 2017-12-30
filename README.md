# meshcheck

## Purpose

  Quickly-hacked together mesh viewer that displays labels for
  vertices and faces. Intended as a visual aid for developing mesh
  modeling tools.

## Usage

  Run the program. Copy a JSON representation of the mesh to the
  clipboard. MMB to load mesh. RMB-drag to rotate. Scroll-wheel to
  zoom in/out.

## Input Format

  The input is a simple JSON format that lists vertices and
  faces. Each vertex gets a string label followed by its coordinates,
  and faces refer to vertices by their labels.

  Example:

  """
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
  """

## Dependencies
  - PyFTGL for text rendering
	- On Ubuntu you can get this with:
      $ apt-get install python-setuptools
	  $ easy_install PyFTGL
  - xclip to read the clipboard (not cross-platform.)
	- $ apt-get install xclip

## Status
  As of October 2nd, this has just had a few hours worth of
  development, so it's pretty useless.
