// SPDX-License-Identifier: LGPL-2.1-or-later

#include <gtest/gtest.h>
#include <Base/TimeInfo.h>

TEST(TimeInfo, TestDefault)
{
    Base::TimeInfo ti;
    EXPECT_FALSE(ti.isNull());
}

TEST(TimeInfo, TestNull)
{
    Base::TimeInfo ti(Base::TimeInfo::null());
    EXPECT_TRUE(ti.isNull());
}

TEST(TimeInfo, TestCompare)
{
    Base::TimeInfo ti1;
    Base::TimeInfo ti2(ti1);
    ti2 += std::chrono::seconds(1);
    EXPECT_TRUE(ti1 == ti1);
    EXPECT_TRUE(ti1 != ti2);
    EXPECT_TRUE(ti1 < ti2);
    EXPECT_FALSE(ti1 > ti2);
    EXPECT_TRUE(ti1 <= ti1);
    EXPECT_TRUE(ti1 >= ti1);
}

TEST(TimeInfo, TestDiffTime)
{
    Base::TimeInfo ti1;
    Base::TimeInfo ti2(ti1);
    ti2 += std::chrono::seconds(1000);
    EXPECT_FLOAT_EQ(Base::TimeInfo::diffTimeF(ti1, ti2), 1000.0);
}

TEST(TimeInfo, TestTimeT)
{
    Base::TimeInfo ti;
    std::time_t now = std::time(nullptr);
    ti.setTime_t(now);
    EXPECT_EQ(ti.getTime_t(), now);
    EXPECT_FALSE(ti.isNull());
}

TEST(TimeInfo, TestDiffTimeStr)
{
    Base::TimeInfo ti1;
    Base::TimeInfo ti2(ti1);
    ti2 += std::chrono::seconds(5);
    std::string diff = Base::TimeInfo::diffTime(ti1, ti2);
    double diff_val = std::stod(diff);
    EXPECT_NEAR(diff_val, 5.0, 0.1);
}

TEST(TimeInfo, TestTimeElapsed)
{
    Base::TimeElapsed te1;
    Base::TimeElapsed te2(te1);
    te2 += std::chrono::milliseconds(500);
    EXPECT_NEAR(Base::TimeElapsed::diffTimeF(te1, te2), 0.5, 0.05);

    std::string diff = Base::TimeElapsed::diffTime(te1, te2);
    double diff_val = std::stod(diff);
    EXPECT_NEAR(diff_val, 0.5, 0.05);
}

TEST(TimeInfo, TestTimeTracker)
{
    {
        Base::TimeTracker tracker("TestTracker");
        tracker.checkpoint("First");
    }
}
