#include <gtest/gtest.h>

#include <Base/Axis.h>
#include <Base/Placement.h>
#include <Base/Rotation.h>

#include <src/App/InitApplication.h>

class Axis: public ::testing::Test
{
protected:
    static void SetUpTestSuite()
    {
        tests::initApplication();
    }
};

TEST_F(Axis, TestDefault)
{
    Base::Axis axis;
    EXPECT_EQ(axis.getBase(), Base::Vector3d());
    EXPECT_EQ(axis.getDirection(), Base::Vector3d());
}

TEST_F(Axis, TestCustom)
{
    Base::Axis axis(Base::Vector3d(0, 0, 1), Base::Vector3d(1, 1, 1));
    EXPECT_EQ(axis.getBase(), Base::Vector3d(0, 0, 1));
    EXPECT_EQ(axis.getDirection(), Base::Vector3d(1, 1, 1));
}

TEST_F(Axis, TestSetter)
{
    Base::Axis axis;
    axis.setBase(Base::Vector3d(0, 0, 1));
    axis.setDirection(Base::Vector3d(1, 1, 1));
    EXPECT_EQ(axis.getBase(), Base::Vector3d(0, 0, 1));
    EXPECT_EQ(axis.getDirection(), Base::Vector3d(1, 1, 1));
}

TEST_F(Axis, TestAssign)
{
    Base::Axis axis;
    Base::Axis move;
    axis.setBase(Base::Vector3d(0, 0, 1));
    axis.setDirection(Base::Vector3d(1, 1, 1));
    move = std::move(axis);  // NOLINT
    EXPECT_EQ(move.getBase(), Base::Vector3d(0, 0, 1));
    EXPECT_EQ(move.getDirection(), Base::Vector3d(1, 1, 1));
}

TEST_F(Axis, TestReverse)
{
    Base::Axis axis(Base::Vector3d(0, 0, 1), Base::Vector3d(1, 1, 1));
    axis.reverse();
    EXPECT_EQ(axis.getBase(), Base::Vector3d(0, 0, 1));
    EXPECT_EQ(axis.getDirection(), Base::Vector3d(-1, -1, -1));
}

TEST_F(Axis, TestReversed)
{
    Base::Axis axis(Base::Vector3d(0, 0, 1), Base::Vector3d(1, 1, 1));
    Base::Axis rev(axis.reversed());
    EXPECT_EQ(axis.getDirection(), Base::Vector3d(1, 1, 1));
    EXPECT_EQ(rev.getBase(), Base::Vector3d(0, 0, 1));
    EXPECT_EQ(rev.getDirection(), Base::Vector3d(-1, -1, -1));
}

TEST_F(Axis, TestMove)
{
    Base::Axis axis(Base::Vector3d(0, 0, 1), Base::Vector3d(1, 1, 1));
    axis.move(Base::Vector3d(1, 2, 3));
    EXPECT_EQ(axis.getBase(), Base::Vector3d(1, 2, 4));
    EXPECT_EQ(axis.getDirection(), Base::Vector3d(1, 1, 1));
}

TEST_F(Axis, TestMult)
{
    Base::Axis axis(Base::Vector3d(0, 0, 1), Base::Vector3d(0, 0, 1));
    axis *= Base::Placement(Base::Vector3d(1, 1, 1), Base::Rotation(1, 0, 0, 0));
    EXPECT_EQ(axis.getBase(), Base::Vector3d(1, 1, 0));
    EXPECT_EQ(axis.getDirection(), Base::Vector3d(0, 0, -1));
}

TEST_F(Axis, TestComparison)
{
    Base::Axis a1(Base::Vector3d(0, 0, 1), Base::Vector3d(1, 0, 0));
    Base::Axis a2(Base::Vector3d(0, 0, 1), Base::Vector3d(1, 0, 0));
    Base::Axis a3(Base::Vector3d(0, 0, 2), Base::Vector3d(1, 0, 0));
    Base::Axis a4(Base::Vector3d(0, 0, 1), Base::Vector3d(0, 1, 0));

    EXPECT_TRUE(a1 == a2);
    EXPECT_FALSE(a1 == a3);
    EXPECT_FALSE(a1 == a4);

    EXPECT_FALSE(a1 != a2);
    EXPECT_TRUE(a1 != a3);
    EXPECT_TRUE(a1 != a4);
}

TEST_F(Axis, TestMultConst)
{
    Base::Axis axis(Base::Vector3d(0, 0, 1), Base::Vector3d(0, 0, 1));
    Base::Placement plm(Base::Vector3d(1, 1, 1), Base::Rotation(1, 0, 0, 0));
    Base::Axis res = axis * plm;

    EXPECT_EQ(res.getBase(), Base::Vector3d(1, 1, 0));
    EXPECT_EQ(res.getDirection(), Base::Vector3d(0, 0, -1));
    
    // Original axis remains unchanged
    EXPECT_EQ(axis.getBase(), Base::Vector3d(0, 0, 1));
    EXPECT_EQ(axis.getDirection(), Base::Vector3d(0, 0, 1));
}

