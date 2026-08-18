#include <gtest/gtest.h>
#include <Base/Placement.h>
#include <Base/ViewProj.h>

TEST(ViewProj, TestViewProjMatrix)
{
    Base::Matrix4D mat;
    Base::ViewProjMatrix proj(mat);

    EXPECT_TRUE(proj.isValid());

    Base::Vector3d vec(1, 2, 3);
    EXPECT_EQ(proj(vec), Base::Vector3d(1, 1.5, 2));
    EXPECT_EQ(proj.inverse(Base::Vector3d(1, 1.5, 2)), vec);

    // Test float version
    Base::Vector3f vecf(1.0f, 2.0f, 3.0f);
    EXPECT_EQ(proj(vecf), Base::Vector3f(1.0f, 1.5f, 2.0f));
    EXPECT_EQ(proj.inverse(Base::Vector3f(1.0f, 1.5f, 2.0f)), vecf);
}

TEST(ViewProj, TestViewOrthoProjMatrix)
{
    Base::Matrix4D mat;
    Base::ViewOrthoProjMatrix proj(mat);

    EXPECT_TRUE(proj.isValid());

    Base::Vector3d vec(1, 2, 3);
    EXPECT_EQ(proj(vec), vec);
    EXPECT_EQ(proj.inverse(vec), vec);

    // Test float version
    Base::Vector3f vecf(1.0f, 2.0f, 3.0f);
    EXPECT_EQ(proj(vecf), vecf);
    EXPECT_EQ(proj.inverse(vecf), vecf);
}

TEST(ViewProj, TestTransformAndComposition)
{
    Base::Matrix4D mat;
    Base::ViewProjMatrix proj(mat);

    // Test default transform
    EXPECT_EQ(proj.getTransform(), Base::Matrix4D());

    // Test setTransform
    Base::Matrix4D transform;
    transform.move(Base::Vector3d(1, 1, 1));
    proj.setTransform(transform);
    EXPECT_EQ(proj.getTransform(), transform);

    // Test projection composition
    Base::Matrix4D composed = proj.getComposedProjectionMatrix();
    // composed = projection_matrix * transform.
    // proj.getProjectionMatrix() should return the original identity mat.
    EXPECT_EQ(composed, transform);

    // Test transformation of input coordinates:
    // vec = (1, 2, 3) -> transform shifts it to (2, 3, 4)
    // then ViewProjMatrix (ortho) scales by 0.5 and shifts by 0.5 -> (1.5, 2.0, 2.5)
    Base::Vector3d vec(1, 2, 3);
    EXPECT_EQ(proj(vec), Base::Vector3d(1.5, 2.0, 2.5));
}

TEST(ViewProj, TestPerspectiveProjection)
{
    Base::Matrix4D mat;
    // Set perspective-like values in the last row to make it non-orthographic
    mat[3][0] = 0.1;
    mat[3][1] = 0.2;
    mat[3][2] = 0.3;
    mat[3][3] = 1.0;

    Base::ViewProjMatrix proj(mat);
    Base::Vector3d vec(1, 2, 3);
    Base::Vector3d projected = proj(vec);
    
    // Check that we can map back using inverse
    Base::Vector3d reconstructed = proj.inverse(projected);
    EXPECT_NEAR(reconstructed.x, vec.x, 1e-7);
    EXPECT_NEAR(reconstructed.y, vec.y, 1e-7);
    EXPECT_NEAR(reconstructed.z, vec.z, 1e-7);

    // Float version
    Base::Vector3f vecf(1.0f, 2.0f, 3.0f);
    Base::Vector3f projectedf = proj(vecf);
    Base::Vector3f reconstructedf = proj.inverse(projectedf);
    EXPECT_NEAR(reconstructedf.x, vecf.x, 1e-5);
    EXPECT_NEAR(reconstructedf.y, vecf.y, 1e-5);
    EXPECT_NEAR(reconstructedf.z, vecf.z, 1e-5);
}

