#include <gtest/gtest.h>

#include <Base/Builder3D.h>

TEST(Builder3D, openInventor)
{
    Base::Builder3D builder;
    builder.beginSeparator();
    builder.endSeparator();
}

TEST(Builder3D, ColorRGB)
{
    // Default constructor
    Base::ColorRGB c1;
    EXPECT_FLOAT_EQ(c1.red(), 1.0f);
    EXPECT_FLOAT_EQ(c1.green(), 1.0f);
    EXPECT_FLOAT_EQ(c1.blue(), 1.0f);

    // Value constructor with clamped values
    Base::ColorRGB c2(0.5f, 2.0f, -1.5f);
    EXPECT_FLOAT_EQ(c2.red(), 0.5f);
    EXPECT_FLOAT_EQ(c2.green(), 1.0f);
    EXPECT_FLOAT_EQ(c2.blue(), -1.0f);
}

TEST(Builder3D, DrawStyle)
{
    Base::DrawStyle ds;
    ds.style = Base::DrawStyle::Style::Filled;
    EXPECT_STREQ(ds.styleAsString(), "FILLED");

    ds.style = Base::DrawStyle::Style::Lines;
    EXPECT_STREQ(ds.styleAsString(), "LINES");

    ds.style = Base::DrawStyle::Style::Points;
    EXPECT_STREQ(ds.styleAsString(), "POINTS");

    ds.style = Base::DrawStyle::Style::Invisible;
    EXPECT_STREQ(ds.styleAsString(), "INVISIBLE");

    ds.linePattern = 0x1234;
    EXPECT_EQ(ds.patternAsString(), "0x1234");
}

TEST(Builder3D, VertexOrdering)
{
    Base::VertexOrdering vo;
    vo.ordering = Base::VertexOrdering::Ordering::UnknownOrdering;
    EXPECT_STREQ(vo.toString(), "UNKNOWN_ORDERING");

    vo.ordering = Base::VertexOrdering::Ordering::Clockwise;
    EXPECT_STREQ(vo.toString(), "CLOCKWISE");

    vo.ordering = Base::VertexOrdering::Ordering::CounterClockwise;
    EXPECT_STREQ(vo.toString(), "COUNTERCLOCKWISE");
}

TEST(Builder3D, ShapeType)
{
    Base::ShapeType st;
    st.type = Base::ShapeType::Type::UnknownShapeType;
    EXPECT_STREQ(st.toString(), "UNKNOWN_SHAPE_TYPE");

    st.type = Base::ShapeType::Type::Convex;
    EXPECT_STREQ(st.toString(), "SOLID");
}

TEST(Builder3D, BindingElement)
{
    Base::BindingElement be;
    be.value = Base::BindingElement::Binding::Overall;
    EXPECT_STREQ(be.bindingAsString(), "OVERALL");

    be.value = Base::BindingElement::Binding::PerPart;
    EXPECT_STREQ(be.bindingAsString(), "PER_PART");

    be.value = Base::BindingElement::Binding::PerPartIndexed;
    EXPECT_STREQ(be.bindingAsString(), "PER_PART_INDEXED");

    be.value = Base::BindingElement::Binding::PerFace;
    EXPECT_STREQ(be.bindingAsString(), "PER_FACE");

    be.value = Base::BindingElement::Binding::PerFaceIndexed;
    EXPECT_STREQ(be.bindingAsString(), "PER_FACE_INDEXED");

    be.value = Base::BindingElement::Binding::PerVertex;
    EXPECT_STREQ(be.bindingAsString(), "PER_VERTEX");

    be.value = Base::BindingElement::Binding::PerVertexIndexed;
    EXPECT_STREQ(be.bindingAsString(), "PER_VERTEX_INDEXED");
}

TEST(Builder3D, PolygonOffset)
{
    Base::PolygonOffset po;
    po.style = Base::PolygonOffset::Style::Filled;
    EXPECT_STREQ(po.styleAsString(), "FILLED");

    po.style = Base::PolygonOffset::Style::Lines;
    EXPECT_STREQ(po.styleAsString(), "LINES");

    po.style = Base::PolygonOffset::Style::Points;
    EXPECT_STREQ(po.styleAsString(), "POINTS");
}

