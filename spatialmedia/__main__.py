#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2016 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Spatial Media Metadata Injector

Tool for examining and injecting spatial media metadata in MP4/MOV files.
"""

import argparse
import os
import re
import sys

path = os.path.dirname(sys.modules[__name__].__file__)
path = os.path.join(path, '..')
sys.path.insert(0, path)
from spatialmedia import metadata_utils


def console(contents):
  print(contents)


def main():
  """Main function for printing and injecting spatial media metadata."""

  parser = argparse.ArgumentParser(
      usage=
      "%(prog)s [options] [files...]\n\nBy default prints out spatial media "
      "metadata from specified files.")
  parser.add_argument(
      "-i",
      "--inject",
      action="store_true",
      help=
      "injects spatial media metadata into the first file specified (.mp4 or "
      ".mov) and saves the result to the second file specified")
  video_group = parser.add_argument_group("Spherical Video")
  video_group.add_argument(
    "-p",
    "--projection",
    action="store",
    dest="projection",
    metavar="PROJECTION",
    choices=["equirectangular", "cubemap", "single_fish_eye", "dual_fish_eye"],
    default="equirectangular",
    help=
        "projection (equirectangular | top-cubemap | single_fish_eye | \
        dual_fish_eye)"
  )
  video_group.add_argument(
    "-fov",
    "--fov",
    action="store",
    dest="fov",
    metavar="FOV",
    default=None,
    help="Original FOV of the single/dual_fish_eye projections"
  )
  video_group.add_argument("-s",
                           "--stereo",
                           action="store",
                           dest="stereo_mode",
                           metavar="STEREO-MODE",
                           choices=["none", "top-bottom", "left-right"],
                           default="none",
                           help="stereo mode (none | top-bottom | left-right)")
  video_group.add_argument(
      "-c",
      "--crop",
      action="store",
      default=None,
      help=
      "crop region. Must specify 6 integers in the form of \"w:h:f_w:f_h:x:y\""
      " where w=CroppedAreaImageWidthPixels h=CroppedAreaImageHeightPixels "
      "f_w=FullPanoWidthPixels f_h=FullPanoHeightPixels "
      "x=CroppedAreaLeftPixels y=CroppedAreaTopPixels")
  audio_group = parser.add_argument_group("Spatial Audio")
  audio_group.add_argument(
      "-a",
      "--spatial-audio",
      action="store_true",
      help=
      "spatial audio. First-order periphonic ambisonics with ACN channel "
      "ordering and SN3D normalization")
  parser.add_argument("file", nargs="+", help="input/output files")

  args = parser.parse_args()

  if args.inject:
    if len(args.file) != 2:
      console("Injecting metadata requires both an input file and output file.")
      return

    metadata = metadata_utils.Metadata()
    metadata.video = metadata_utils.generate_spherical_xml(args.projection,
                                                           args.fov,
                                                           args.stereo_mode,
                                                           args.crop)

    if args.spatial_audio:
      metadata.audio = metadata_utils.SPATIAL_AUDIO_DEFAULT_METADATA

    if metadata.video:
      metadata_utils.inject_metadata(args.file[0], args.file[1], metadata,
                                     console)
    else:
      console("Failed to generate metadata.")
    return

  if len(args.file) > 0:
    for input_file in args.file:
      metadata_utils.parse_metadata(input_file, console)
    return

  parser.print_help()
  return


if __name__ == "__main__":
  main()
