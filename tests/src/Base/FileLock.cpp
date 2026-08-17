// SPDX-License-Identifier: LGPL-2.1-or-later

#include <gtest/gtest.h>

#include <Base/FileInfo.h>
#include <Base/FileLock.h>

#include <filesystem>
#include <string>

TEST(FileLockTest, TryLockZeroSucceedsWhenAvailable)
{
#if defined(__EMSCRIPTEN__)
    GTEST_SKIP() << "File locking is a no-op in Emscripten/WASM (single-process).";
#endif

    std::string fn = Base::FileInfo::getTempFileName();
    fn.append(".lock");

    Base::FileLock lockFile1(fn);
    EXPECT_TRUE(lockFile1.tryLock(0));
    EXPECT_TRUE(lockFile1.isLocked());
    lockFile1.unlock();

    Base::FileLock lockFile2(fn);
    EXPECT_TRUE(lockFile2.tryLock(0));
    lockFile2.unlock();

    std::error_code ec;
    (void)std::filesystem::remove(std::filesystem::path(fn), ec);
}

TEST(FileLockTest, LockBlockingSucceeds)
{
#if defined(__EMSCRIPTEN__)
    GTEST_SKIP() << "File locking is a no-op in Emscripten/WASM.";
#endif

    std::string fn = Base::FileInfo::getTempFileName();
    fn.append(".lock");

    Base::FileLock lockFile1(fn);
    EXPECT_TRUE(lockFile1.lock());
    EXPECT_TRUE(lockFile1.isLocked());
    
    // Unlock and lock again
    lockFile1.unlock();
    EXPECT_FALSE(lockFile1.isLocked());
    EXPECT_TRUE(lockFile1.lock());
    lockFile1.unlock();

    std::error_code ec;
    (void)std::filesystem::remove(std::filesystem::path(fn), ec);
}

TEST(FileLockTest, TryLockFailsOnAlreadyLockedFile)
{
#if defined(__EMSCRIPTEN__)
    GTEST_SKIP() << "File locking is a no-op in Emscripten/WASM.";
#endif

    std::string fn = Base::FileInfo::getTempFileName();
    fn.append(".lock");

    Base::FileLock lockFile1(fn);
    EXPECT_TRUE(lockFile1.lock());

    Base::FileLock lockFile2(fn);
    EXPECT_FALSE(lockFile2.tryLock(50));
    EXPECT_FALSE(lockFile2.isLocked());

    lockFile1.unlock();
    
    // Now lockFile2 should succeed
    EXPECT_TRUE(lockFile2.tryLock(0));
    EXPECT_TRUE(lockFile2.isLocked());
    lockFile2.unlock();

    std::error_code ec;
    (void)std::filesystem::remove(std::filesystem::path(fn), ec);
}
