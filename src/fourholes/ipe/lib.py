import functools
import sys
from pathlib import Path

import cppyy

cppyy.load_library("ipe")
cppyy.include("ipelib.h")
cppyy.include("ipeiml.h")

ipe = cppyy.gbl.ipe
std = cppyy.gbl.std

ipe.Platform.initLib(ipe.IPELIB_VERSION)
ipe.Platform.setDebug(True)

ipe.String.__str__ = ipe.String.z
ipe.String.__repr__ = lambda self: 'ipe.String(%r)' % str(self)


# def enum(e):
#     return SimpleNamespace({k: v for k, v in e.__dict__.items() if isinstance(v, e)})

# %%

def set_properties(obj, kwargs):
    rotation = kwargs.pop("rotation", None)
    if rotation is not None:
        obj.setMatrix(ipe.Matrix(ipe.Linear(ipe.Angle(rotation * ipe.IPE_PI))))
    for prop, val in kwargs.items():
        if val is None:
            continue
        setter = getattr(obj, "set" + prop[0].capitalize() + prop[1:])
        if isinstance(val,
                        (ipe.Color, ipe.TFillRule, ipe.THorizontalAlignment, ipe.TLineCap, ipe.TLineJoin, ipe.TPathMode,
                         ipe.TPinned, ipe.TSplineType, ipe.TTransformations)):
            setter(ipe.Attribute(val))
        elif isinstance(val, str):
            setter(ipe.Attribute(symbolic=True, name=val))
        elif isinstance(val, int):
            setter(ipe.Attribute(ipe.Fixed(val)))
        elif isinstance(val, float):
            setter(ipe.Attribute(ipe.Fixed.fromDouble(val)))
        else:
            setter(val)
    return obj


def make_arc(start, stop, scale=100, center=(0, 0), arrow=None, arrowsize="normal", closed=False, **kwargs):
    a = ipe.Path(ipe.AllAttributes(), ipe.Shape(ipe.Vector(*center), scale, start * ipe.IPE_PI, stop * ipe.IPE_PI),
                 True)
    if closed:
        sp = a.shape().subPath(0)
        sp.appendSegment(sp.segment(0).last(), ipe.Vector(*center))
        sp.setClosed(True)
    # arrow = "arrow/normal(spx)"
    if arrow:
        a.setArrow(True, ipe.Attribute(True, arrow), ipe.Attribute(True, arrowsize))
    # a.setPathMode(ipe.EStrokedAndFilled)
    a.__python_owns__ = False
    return set_properties(a, kwargs)


def make_segment(start=(0, 0), stop=(100, 0), **kwargs):
    p = ipe.Path(ipe.AllAttributes(), ipe.Shape(ipe.Segment(ipe.Vector(*start), ipe.Vector(*stop))), True)
    p.__python_owns__ = False
    return set_properties(p, kwargs)


def make_node(name="mark/fdisk(sfx)", pos=(0, 0), **kwargs):
    r = ipe.Reference(ipe.AllAttributes(), ipe.Attribute(True, name), ipe.Vector(*pos))
    r.__python_owns__ = False
    return set_properties(r, kwargs)


def make_text(text, pos=(0, 0), **kwargs):
    t = ipe.Text(ipe.AllAttributes(), ipe.String(text), ipe.Vector(*pos), ipe.Text.TextType.ELabel)
    t.setHorizontalAlignment(ipe.EAlignHCenter)
    t.setVerticalAlignment(ipe.EAlignVCenter)
    t.__python_owns__ = False
    return set_properties(t, kwargs)


def make_group(iter, translate=None):
    g = ipe.Group()
    g.__python_owns__ = False
    for obj in iter:
        g.push_back(obj)
    if translate:
        g.setMatrix(ipe.Matrix(ipe.Vector(*translate)))
    return g


# %%


old_append = ipe.Page.append


@functools.wraps(old_append)
def new_append(self, *args, **kwargs):
    if len(args) == 1 and not kwargs:
        # signature is (select, layer, obj)
        old_append(self, ipe.TSelect.ENotSelected, 0, *args)
    else:
        old_append(self, *args, **kwargs)
    return self


ipe.Page.append = new_append


# %%

def make_document():
    doc = ipe.Document()
    doc.cascade().insert(0, get_style("/usr/share/ipe/7.2.30/styles/basic.isy"))
    # doc.cascade().insert(0, get_style(ipe.Platform.folder(ipe.IpeFolder.FolderStyles, "basic.isy")))
    return doc


def make_page():
    page = ipe.Page()
    page.addLayer()
    page.insertView(0, page.layer(0))
    page.setVisible(0, page.layer(0), True)
    page.__python_owns__ = False
    return page
    # doc.push_back(page)


def save(doc, path=None, flags=ipe.SaveFlag.SaveNormal):
    if not path:
        path = sys.modules['__main__'].__file__
    path = Path(path)
    doc.runLatex(str(path.with_suffix(".tex")))
    if path.suffix == ".ipe":
        return doc.save(str(path), ipe.FileFormat.Xml, flags)
    elif path.suffix == ".pdf":
        return doc.save(str(path), ipe.FileFormat.Pdf, flags)
    else:
        return doc.save(str(path.with_suffix(".ipe")), ipe.FileFormat.Xml, flags) \
            and doc.save(str(path.with_suffix(".pdf")), ipe.FileFormat.Pdf, flags)


def get_style(path):
    fd = ipe.Platform.fopen(path, "rb")
    if not fd:
        raise IOError("Could not open %s" % path)
    src = ipe.FileSource(fd)
    style = ipe.ImlParser(src).parseStyleSheet()
    std.fclose(fd)
    if not style:
        raise IOError("Could not parse style %s" % path)
    style.__python_owns__ = False
    return style
