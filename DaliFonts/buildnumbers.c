/* xdaliclock - a melting digital clock
 * Copyright (c) 1991-2009 Jamie Zawinski <jwz@jwz.org>
 * Extended 2015 by Robin Müller-Cajar <robinmc@mailbox.org>
 *
 * Permission to use, copy, modify, distribute, and sell this software and its
 * documentation for any purpose is hereby granted without fee, provided that
 * the above copyright notice appear in all copies and that both that
 * copyright notice and this permission notice appear in supporting
 * documentation.  No representations are made about the suitability of this
 * software for any purpose.  It is provided "as is" without express or
 * implied warranty.
 *
 * This is a stripped-down version of OSX/digital.c for converting the font
 * pixmaps to a JavaScript representation of `struct raw_number'.
 */

#ifdef HAVE_CONFIG_H
# include "config.h"
#endif

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <time.h>
#include <sys/time.h>

#include "xdaliclock.h"

typedef unsigned short POS;
typedef unsigned char BOOL;

#ifdef BUILTIN_FONTS

/* static int use_builtin_font; */

struct raw_number {
  const unsigned char *bits;
  POS width, height;
};

#endif /* BUILTIN_FONTS */

#ifdef BUILTIN_FONTS

#define FONT(X)								\
 static const struct raw_number numbers_ ## X [] = {			\
  { zero  ## X ## _bits,  zero ## X ## _width,  zero ## X ## _height }, \
  { one   ## X ## _bits,   one ## X ## _width,   one ## X ## _height }, \
  { two   ## X ## _bits,   two ## X ## _width,   two ## X ## _height }, \
  { three ## X ## _bits, three ## X ## _width, three ## X ## _height }, \
  { four  ## X ## _bits,  four ## X ## _width,  four ## X ## _height }, \
  { five  ## X ## _bits,  five ## X ## _width,  five ## X ## _height }, \
  { six   ## X ## _bits,   six ## X ## _width,   six ## X ## _height }, \
  { seven ## X ## _bits, seven ## X ## _width, seven ## X ## _height }, \
  { eight ## X ## _bits, eight ## X ## _width, eight ## X ## _height }, \
  { nine  ## X ## _bits,  nine ## X ## _width,  nine ## X ## _height }, \
  { colon ## X ## _bits, colon ## X ## _width, colon ## X ## _height }, \
  { slash ## X ## _bits, slash ## X ## _width, slash ## X ## _height }, \
  { 0, }								\
}

# include "zeroA.xbm"
# include "oneA.xbm"
# include "twoA.xbm"
# include "threeA.xbm"
# include "fourA.xbm"
# include "fiveA.xbm"
# include "sixA.xbm"
# include "sevenA.xbm"
# include "eightA.xbm"
# include "nineA.xbm"
# include "colonA.xbm"
# include "slashA.xbm"
FONT(A);

# include "zeroB.xbm"
# include "oneB.xbm"
# include "twoB.xbm"
# include "threeB.xbm"
# include "fourB.xbm"
# include "fiveB.xbm"
# include "sixB.xbm"
# include "sevenB.xbm"
# include "eightB.xbm"
# include "nineB.xbm"
# include "colonB.xbm"
# include "slashB.xbm"
FONT(B);

# include "zeroB2.xbm"
# include "oneB2.xbm"
# include "twoB2.xbm"
# include "threeB2.xbm"
# include "fourB2.xbm"
# include "fiveB2.xbm"
# include "sixB2.xbm"
# include "sevenB2.xbm"
# include "eightB2.xbm"
# include "nineB2.xbm"
# include "colonB2.xbm"
# include "slashB2.xbm"
FONT(B2);

# include "zeroC2.xbm"
# include "oneC2.xbm"
# include "twoC2.xbm"
# include "threeC2.xbm"
# include "fourC2.xbm"
# include "fiveC2.xbm"
# include "sixC2.xbm"
# include "sevenC2.xbm"
# include "eightC2.xbm"
# include "nineC2.xbm"
# include "colonC2.xbm"
# include "slashC2.xbm"
FONT(C2);

# include "zeroC3.xbm"
# include "oneC3.xbm"
# include "twoC3.xbm"
# include "threeC3.xbm"
# include "fourC3.xbm"
# include "fiveC3.xbm"
# include "sixC3.xbm"
# include "sevenC3.xbm"
# include "eightC3.xbm"
# include "nineC3.xbm"
# include "colonC3.xbm"
# include "slashC3.xbm"
FONT(C3);

# include "zeroD3.xbm"
# include "oneD3.xbm"
# include "twoD3.xbm"
# include "threeD3.xbm"
# include "fourD3.xbm"
# include "fiveD3.xbm"
# include "sixD3.xbm"
# include "sevenD3.xbm"
# include "eightD3.xbm"
# include "nineD3.xbm"
# include "colonD3.xbm"
# include "slashD3.xbm"
FONT(D3);

# include "zeroD4.xbm"
# include "oneD4.xbm"
# include "twoD4.xbm"
# include "threeD4.xbm"
# include "fourD4.xbm"
# include "fiveD4.xbm"
# include "sixD4.xbm"
# include "sevenD4.xbm"
# include "eightD4.xbm"
# include "nineD4.xbm"
# include "colonD4.xbm"
# include "slashD4.xbm"
FONT(D4);

# include "zeroE.xbm"
# include "oneE.xbm"
# include "twoE.xbm"
# include "threeE.xbm"
# include "fourE.xbm"
# include "fiveE.xbm"
# include "sixE.xbm"
# include "sevenE.xbm"
# include "eightE.xbm"
# include "nineE.xbm"
# include "colonE.xbm"
# include "slashE.xbm"
FONT(E);

#endif /* BUILTIN_FONTS */

#undef countof
#define countof(x) (sizeof((x))/sizeof(*(x)))

/* Number of horizontal segments/line.  Enlarge this if you are trying
   to use a font that is too "curvy" for XDaliClock to cope with.
   This code was sent to me by Dan Wallach <c169-bg@auriga.berkeley.edu>.
   I'm highly opposed to ever using statically-sized arrays, but I don't
   really feel like hacking on this code enough to clean it up.
 */
#ifndef MAX_SEGS_PER_LINE
# define MAX_SEGS_PER_LINE 5
#endif

struct scanline {
  POS left[MAX_SEGS_PER_LINE], right[MAX_SEGS_PER_LINE];
};

struct frame {
  struct scanline scanlines [1]; /* scanlines are contiguous here */
};


/* The runtime settings (some initialized from system prefs, but changable.)
 */
struct render_state {

  int char_width, char_height, colon_width;

  struct frame *base_frames [12];
};


static struct frame *
make_blank_frame (int width, int height)
{
  int size = sizeof (struct frame) + (sizeof (struct scanline) * (height - 1));
  struct frame *frame;
  int x, y;

  frame = (struct frame *) calloc (size, 1);
  for (y = 0; y < height; y++)
    for (x = 0; x < MAX_SEGS_PER_LINE; x++)
      frame->scanlines[y].left [x] = frame->scanlines[y].right [x] = width / 2;
  return frame;
}


static struct frame *
number_to_frame (const unsigned char *bits, int width, int height)
{
  int x, y;
  struct frame *frame;
  POS *left, *right;

  frame = make_blank_frame (width, height);

  for (y = 0; y < height; y++)
    {
      int seg, end;
      x = 0;
# define GETBIT(bits,x,y) \
         (!! ((bits) [((y) * ((width+7) >> 3)) + ((x) >> 3)] \
              & (1 << ((x) & 7))))

      left = frame->scanlines[y].left;
      right = frame->scanlines[y].right;

      for (seg = 0; seg < MAX_SEGS_PER_LINE; seg++)
        left [seg] = right [seg] = width / 2;

      for (seg = 0; seg < MAX_SEGS_PER_LINE; seg++)
        {
          for (; x < width; x++)
            if (GETBIT (bits, x, y)) break;
          if (x == width) break;
          left [seg] = x;
          for (; x < width; x++)
            if (! GETBIT (bits, x, y)) break;
          right [seg] = x;
        }

      for (; x < width; x++)
        if (GETBIT (bits, x, y))
          {
            /* This means the font is too curvy.  Increase MAX_SEGS_PER_LINE
               and recompile. */
            fprintf (stderr, "%s: font is too curvy\n", progname);
            exit (-1);
          }

      /* If there were any segments on this line, then replicate the last
         one out to the end of the line.  If it's blank, leave it alone,
         meaning it will be a 0-pixel-wide line down the middle.
       */
      end = seg;
      if (end > 0)
        for (; seg < MAX_SEGS_PER_LINE; seg++)
          {
            left [seg] = left [end-1];
            right [seg] = right [end-1];
          }

# undef GETBIT
    }

  return frame;
}



static void
init_numbers (dali_config *c, int size)
{
  struct render_state *state = c->render_state;
  int i;
#ifdef BUILTIN_FONTS
  const struct raw_number *raw;

  switch (size)
    {
    case 0: raw = numbers_E;  break;
    case 1: raw = numbers_D4; break;
    case 2: raw = numbers_D3; break;
    case 3: raw = numbers_C3; break;
    case 4: raw = numbers_C2; break;
    case 5: raw = numbers_B2; break;
    case 6: raw = numbers_B; break;
    case 7: raw = numbers_A; break;
    default: abort(); break;
    }

  state->char_width  = raw[0].width;
  state->char_height = raw[0].height;
  state->colon_width = raw[10].width;

  for (i = 0; i < countof(state->base_frames); i++)
    state->base_frames [i] =
      number_to_frame (raw[i].bits, raw[i].width, raw[i].height);
#endif /* BUILTIN_FONTS */
}


static void
print_numbers (dali_config *c, int font)
{
  int i;
  struct render_state *state = c->render_state;
  int width  = state->char_width;
  int height = state->char_height;
  int cw     = state->colon_width;

  fprintf (stdout, "{\n");
  fprintf (stdout, " \"font_number\"   \t: %d,\n", font);
  fprintf (stdout, " \"char_width\"    \t: %d,\n", width);
  fprintf (stdout, " \"char_height\"   \t: %d,\n", height);
  fprintf (stdout, " \"colon_width\"   \t: %d,\n", cw);
  fprintf (stdout, " \"segments\":\n");
  fprintf (stdout, "      [\n");

  for (i = 0; i < countof(state->base_frames); i++)
    {
      struct frame *frame = state->base_frames[i];
      int x, y;
      fprintf (stdout, "       [\n");
      for (y = 0; y < height; y++)
        {
          int ol = -99999, or = -99999;
          fprintf (stdout, "\t[");
          for (x = 0; x < MAX_SEGS_PER_LINE; x++)
            {
              int left  = frame->scanlines[y].left  [x];
              int right = frame->scanlines[y].right [x];
              if (ol == left && or == right) continue;
              ol = left;
              or = right;
              if (x != 0) fprintf (stdout, ",");
              fprintf (stdout, "[%d,%d]", left, right);
            }
          fprintf (stdout, "],\n");
        }
      fprintf (stdout, "       ],\n");
    }
  fprintf (stdout, "      ]\n");
  fprintf (stdout, "}\n");
}


char *progname;

int
main (int argc, char **argv)
{
  dali_config C, *c = &C;
  int font;

  progname = argv[0];
  if (argc != 2)
    {
      fprintf (stderr, "usage: %s font > out.json\n", progname);
      exit (1);
    }

  c->render_state = (struct render_state *)
    calloc (1, sizeof (struct render_state));

  font = atoi (argv[1]);
  init_numbers (c, font);
  print_numbers (c, font);

  return 0;
}
