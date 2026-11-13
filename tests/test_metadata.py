from src.objects.metadata import Exif, IccProfile, Jfif, Mpf, XmpExtensionFragment, XmpStandard, get

exif = b"Exif\x00\x00II*"
icc_profile = b"ICC_PROFILE\x00\x01\x01\x00\x00\x0cHLino"
jfif = b"JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00"
mpf = b"MPF\x00II*"
xmp_extension_fragment = b"http://ns.adobe.com/xmp/extension/\x00090F77BD3AD151B65A612E8C8B8CC53E\x00\x01\x08\xc6\x00\x00\x00\x00"
xmp_standard = b"http://ns.adobe.com/xap/1.0/\x00<x:xmpmeta xmlns:x='adobe:ns:meta/'></x:xmpmeta>"


def test_metadata_exif():
    assert Exif.has_signature(exif) == True
    assert Exif.has_signature(icc_profile) == False
    assert Exif.has_signature(jfif) == False
    assert Exif.has_signature(mpf) == False
    assert Exif.has_signature(xmp_extension_fragment) == False
    assert Exif.has_signature(xmp_standard) == False


def test_metadata_icc_profile():
    assert IccProfile.has_signature(exif) == False
    assert IccProfile.has_signature(icc_profile) == True
    assert IccProfile.has_signature(jfif) == False
    assert IccProfile.has_signature(mpf) == False
    assert IccProfile.has_signature(xmp_extension_fragment) == False
    assert IccProfile.has_signature(xmp_standard) == False


def test_metadata_jfif():
    assert Jfif.has_signature(exif) == False
    assert Jfif.has_signature(icc_profile) == False
    assert Jfif.has_signature(jfif) == True
    assert Jfif.has_signature(mpf) == False
    assert Jfif.has_signature(xmp_extension_fragment) == False
    assert Jfif.has_signature(xmp_standard) == False


def test_metadata_mpf():
    assert Mpf.has_signature(exif) == False
    assert Mpf.has_signature(icc_profile) == False
    assert Mpf.has_signature(jfif) == False
    assert Mpf.has_signature(mpf) == True
    assert Mpf.has_signature(xmp_extension_fragment) == False
    assert Mpf.has_signature(xmp_standard) == False


def test_metadata_xmp_extension_fragment():
    assert XmpExtensionFragment.has_signature(exif) == False
    assert XmpExtensionFragment.has_signature(icc_profile) == False
    assert XmpExtensionFragment.has_signature(jfif) == False
    assert XmpExtensionFragment.has_signature(mpf) == False
    assert XmpExtensionFragment.has_signature(xmp_extension_fragment) == True
    assert XmpExtensionFragment.has_signature(xmp_standard) == False


def test_metadata_xmp_standard():
    assert XmpStandard.has_signature(exif) == False
    assert XmpStandard.has_signature(icc_profile) == False
    assert XmpStandard.has_signature(jfif) == False
    assert XmpStandard.has_signature(mpf) == False
    assert XmpStandard.has_signature(xmp_extension_fragment) == False
    assert XmpStandard.has_signature(xmp_standard) == True


def test_get_metadata():
    assert isinstance(get(exif), Exif)
    assert isinstance(get(icc_profile), IccProfile)
    assert isinstance(get(jfif), Jfif)
    assert isinstance(get(mpf), Mpf)
    assert isinstance(get(xmp_extension_fragment), XmpExtensionFragment)
    assert isinstance(get(xmp_standard), XmpStandard)
