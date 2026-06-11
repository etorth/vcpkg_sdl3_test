vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO sabdul-khabir/SDL3_gfx
    REF 0bbee988bb0caa3e98a9d78c7a2d106925c8275a
    SHA512 2d0a37d2c06302d4a1b593eee4c50134d0b0b2f211e92c7ae8bf7e7d1ee730ddd5c99a726f09472a3e7c99715af026108459d0c0e8a15ab12d05c8c5795c017d
    HEAD_REF master
    PATCHES
        fix-cmake.patch
)

vcpkg_cmake_configure(
    SOURCE_PATH "${SOURCE_PATH}"
    OPTIONS
        -DBUILD_TESTS=OFF
)
vcpkg_cmake_install()
vcpkg_copy_pdbs()
vcpkg_fixup_pkgconfig()

file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/include")
file(INSTALL "${SOURCE_PATH}/COPYING"
     DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}"
     RENAME copyright)

