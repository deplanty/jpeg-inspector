from src.objects.metadata import Exif, IccProfile, Jfif, Mpf, XmpExtension, XmpStandard

exif = b"Exif\x00\x00II*"
icc_profile = b"ICC_PROFILE\x00\x01\x01\x00\x00\x0cHLino"
jfif = b"JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00"
mpf = b"MPF\x00II*"
xmp_extension = b"http://ns.adobe.com/xmp/extension/\x00090F7"
xmp_standard = b"http://ns.adobe.com/xap/1.0/\x00<x:xmpmeta xmlns"


def test_metadata_exif():
    assert Exif.has_signature(exif) == True
    assert Exif.has_signature(icc_profile) == False
    assert Exif.has_signature(jfif) == False
    assert Exif.has_signature(mpf) == False
    assert Exif.has_signature(xmp_extension) == False
    assert Exif.has_signature(xmp_standard) == False


def test_metadata_icc_profile():
    assert IccProfile.has_signature(exif) == False
    assert IccProfile.has_signature(icc_profile) == True
    assert IccProfile.has_signature(jfif) == False
    assert IccProfile.has_signature(mpf) == False
    assert IccProfile.has_signature(xmp_extension) == False
    assert IccProfile.has_signature(xmp_standard) == False


def test_metadata_jfif():
    assert Jfif.has_signature(exif) == False
    assert Jfif.has_signature(icc_profile) == False
    assert Jfif.has_signature(jfif) == True
    assert Jfif.has_signature(mpf) == False
    assert Jfif.has_signature(xmp_extension) == False
    assert Jfif.has_signature(xmp_standard) == False


def test_metadata_mpf():
    assert Mpf.has_signature(exif) == False
    assert Mpf.has_signature(icc_profile) == False
    assert Mpf.has_signature(jfif) == False
    assert Mpf.has_signature(mpf) == True
    assert Mpf.has_signature(xmp_extension) == False
    assert Mpf.has_signature(xmp_standard) == False


def test_metadata_xmp_extension():
    assert XmpExtension.has_signature(exif) == False
    assert XmpExtension.has_signature(icc_profile) == False
    assert XmpExtension.has_signature(jfif) == False
    assert XmpExtension.has_signature(mpf) == False
    assert XmpExtension.has_signature(xmp_extension) == True
    assert XmpExtension.has_signature(xmp_standard) == False


def test_metadata_xmp_standard():
    assert XmpStandard.has_signature(exif) == False
    assert XmpStandard.has_signature(icc_profile) == False
    assert XmpStandard.has_signature(jfif) == False
    assert XmpStandard.has_signature(mpf) == False
    assert XmpStandard.has_signature(xmp_extension) == False
    assert XmpStandard.has_signature(xmp_standard) == True
