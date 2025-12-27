# GuARanteed Monochromatic Empty Not-quite-order Type numbers of bichromatic point sets

# Definition
A *structure* is a (closed) subset of the plane that is defined by 4 points of some point set $P$, and that contains no other points from $P$.
We consider five different structures, namely:

- a *cravat*[^1],
  defined by 4 points in convex position, is the convex hull of these 4 points.
- a *necklace*, 
  defined by 4 points in convex position, is the union of two triangles that share exactly two consecutive points.
- a *bowtie*,
  defined by 4 points in convex position, is the symmetric difference of two triangles that share exactly two consecutive points.
- a *skirt*,
  defined by 4 points in non-convex position, is the convex hull of these 4 points.
- a *pant*[^2],
  defined by 4 points in non-convex position, is a non-convex simple 4-gon on these 4 points.

[^1]: As in french 'à la cravate', commonly also called necktie.
[^2]: 'A pant' is actually a viable alternative to 'pants', especially in the [fashion industry](https://grammarphobia.com/blog/2015/11/pants.html).

![The five types of structures: cravat, necklace, bowtie (for convex point sets), and skirt, pant (for non-convex point sets).](img/types.png)

For bicolored point sets, we only consider structures that are monochromatic and contain no additional points of that color within their boundary.
We study whether all large enough bichromatic point sets contain an empty monochromatic structure. 
Formally, given a set $S$ of structures, we define the *GuARanteed Monochromatic Empty Not-quite-order Type number* (shorthand: Garment number) of bichromatic point sets, to be the smallest integer $n$, such that every bichromatic point set of size $n$ contains at least one empty monochromatic structure from $S$.
If we want to say that the Garment number of the set $S=\{\textrm{skirt, bowtie}\}$ is more than 7, we denote this by $\mathcal G(\textrm{skirt}\vee \textrm{bowtie})>7$.

# Lower Bounds via Counter Examples

In the `data/` directory, this repository contains example instances that show the following relations:
- $\mathcal G(\textrm{bowtie}\vee \textrm{pant})>10$
- $\mathcal G(\textrm{necklace}\vee \textrm{pant})>12$
- $\mathcal G(\textrm{cravat}\vee \textrm{pant})>22$
- $\mathcal G(\textrm{cravat}\vee \textrm{skirt})>35$

The example instances can be verified using the `garment` python executable available from this repository:
```bash
pip install git+https://github.com/N-Coder/garment-numbers-colored-point-sets.git
```
Then, to check e.g. the first lower bound, run
```bash
garment data/n10_c2_no_monochromatic_bow_tie.csv --only bowtie --only pant
```
When the optional `render` dependencies (and thereby `cppyy`) as well as a system-wide [`ipelib`](https://ipe.otfried.org/) is intalled,
the instances can also be rendered as ipe figures using the `garment-render` command.

The main function `find_empty_monochromatic_substructures` used for enumerating and checking all possible substructures 
is based on roughly 100 lines of Python code and can be found and easily verified in `src/garment_nrs/lib.py`.
The file `viz_test.py` contains some example code visualizing the enumerated substructures.
