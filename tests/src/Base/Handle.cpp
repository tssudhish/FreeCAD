#include <gtest/gtest.h>
#include <Base/Handle.h>

class Data: public Base::Handled
{
    int myValue {};

public:
    int getValue() const
    {
        return myValue;
    }
    void setValue(int val)
    {
        myValue = val;
    }
};

TEST(Reference, TestNull)
{
    Base::Reference<Data> data;
    EXPECT_EQ(data.getRefCount(), 0);
}

TEST(Reference, TestConstructor)
{
    Base::Reference<Data> data(new Data);
    EXPECT_EQ(data.getRefCount(), 1);
}

TEST(Reference, TestCopy)
{
    Base::Reference<Data> data(new Data);
    Base::Reference<Data> copy(data);
    EXPECT_EQ(data.getRefCount(), 2);
    EXPECT_EQ(copy.getRefCount(), 2);
    EXPECT_EQ(data, copy);
    EXPECT_EQ(data.isValid(), true);
    EXPECT_EQ(copy.isValid(), true);
    EXPECT_EQ(data.isNull(), false);
    EXPECT_EQ(copy.isNull(), false);
}

TEST(Reference, TestAssignRaw)
{
    Base::Reference<Data> data = new Data();
    EXPECT_EQ(data->getValue(), 0);
    EXPECT_EQ(data.getRefCount(), 1);
}

TEST(Reference, TestAssignRef)
{
    Base::Reference<Data> data = new Data();
    Base::Reference<Data> copy;
    copy = data;
    EXPECT_EQ(data.getRefCount(), 2);
    EXPECT_EQ(copy.getRefCount(), 2);
    EXPECT_EQ(data, copy);
    EXPECT_EQ(data.isValid(), true);
    EXPECT_EQ(copy.isValid(), true);
    EXPECT_EQ(data.isNull(), false);
    EXPECT_EQ(copy.isNull(), false);
}

TEST(Reference, TestRefHandle)
{
    Base::Reference<Data> data = new Data();
    data->ref();
    EXPECT_EQ(data.getRefCount(), 2);
    data->unref();
    EXPECT_EQ(data.getRefCount(), 1);
}

TEST(Reference, TestUnrefNoDelete)
{
    Data* raw = new Data();
    raw->ref();
    EXPECT_EQ(raw->getRefCount(), 1);

    // Decrement ref count without deleting the object
    int hasRefs = raw->unrefNoDelete();
    EXPECT_EQ(hasRefs, 0);
    EXPECT_EQ(raw->getRefCount(), 0);

    // Clean up manually since unrefNoDelete didn't delete it
    delete raw;
}

TEST(Reference, TestHandledAssignmentOperator)
{
    Data d1;
    Data d2;
    d1.setValue(42);
    d2.setValue(84);

    d1.ref();
    EXPECT_EQ(d1.getRefCount(), 1);
    EXPECT_EQ(d2.getRefCount(), 0);

    // Assigning handled objects must not assign refcount
    d2 = d1;
    EXPECT_EQ(d1.getRefCount(), 1);
    EXPECT_EQ(d2.getRefCount(), 0);
    
    // Test reference self-assignment
    Base::Reference<Data> ref1(new Data);
    ref1 = ref1;
    EXPECT_EQ(ref1.getRefCount(), 1);
}

