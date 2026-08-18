// SPDX-License-Identifier: LGPL-2.1-or-later

#include <gtest/gtest.h>

#include <Base/Bitmask.h>

enum class TestFlagEnum
{
    Flag0 = 0,
    Flag1 = 1 << 0,
    Flag2 = 1 << 1,
    Flag3 = 1 << 2
};
ENABLE_BITMASK_OPERATORS(TestFlagEnum)

class BitmaskTest: public ::testing::Test
{
};

TEST_F(BitmaskTest, toUnderlyingType)
{
    Base::Flags<TestFlagEnum> flag1 {TestFlagEnum::Flag1};
    auto result = flag1.toUnderlyingType();
    EXPECT_EQ(result, 1);
}

TEST_F(BitmaskTest, bitwiseOperators)
{
    TestFlagEnum f12 = TestFlagEnum::Flag1 | TestFlagEnum::Flag2;
    EXPECT_EQ(static_cast<int>(f12), 3);

    TestFlagEnum f1 = f12 & TestFlagEnum::Flag1;
    EXPECT_EQ(f1, TestFlagEnum::Flag1);

    TestFlagEnum fNot = ~TestFlagEnum::Flag0;
    EXPECT_NE(fNot, TestFlagEnum::Flag0);
}

TEST_F(BitmaskTest, flagsClass)
{
    Base::Flags<TestFlagEnum> flags;
    EXPECT_FALSE(flags.testFlag(TestFlagEnum::Flag1));

    flags.setFlag(TestFlagEnum::Flag1, true);
    EXPECT_TRUE(flags.testFlag(TestFlagEnum::Flag1));
    EXPECT_FALSE(flags.testFlag(TestFlagEnum::Flag2));

    flags.setFlag(TestFlagEnum::Flag2, true);
    EXPECT_TRUE(flags.testFlag(TestFlagEnum::Flag1));
    EXPECT_TRUE(flags.testFlag(TestFlagEnum::Flag2));

    flags.setFlag(TestFlagEnum::Flag1, false);
    EXPECT_FALSE(flags.testFlag(TestFlagEnum::Flag1));
    EXPECT_TRUE(flags.testFlag(TestFlagEnum::Flag2));
    
    Base::Flags<TestFlagEnum> flags2(TestFlagEnum::Flag2);
    EXPECT_TRUE(flags.isEqual(flags2));

    // operator bool
    EXPECT_TRUE(static_cast<bool>(flags2));
    
    Base::Flags<TestFlagEnum> flags0(TestFlagEnum::Flag0);
    EXPECT_FALSE(static_cast<bool>(flags0));
}
