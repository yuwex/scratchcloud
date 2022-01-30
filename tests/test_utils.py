import unittest
from scratchcloud.ext import SegmentDump, BaseCodec
from scratchcloud import errors, CloudClient

class DummyClient:
    def __init__(self, encoder=None, decoder=None, cloud_variables: dict = None):
        self.encoder = encoder
        self.decoder = decoder
        self.cloud_variables = cloud_variables


class TestSegmentDump(unittest.TestCase):

    def test_read(self):
        client = DummyClient(
            BaseCodec().encode,
            BaseCodec().decode,
            cloud_variables={'v1':'10', 'v2':'11', 'v3':'12', 'v4':'13', 'v5':'14', 'v6':'15', 'v7':'0', 'v8':'16', 'v9':'17'})

        # Normal Segment Dumping
        sd = SegmentDump(client, ['v1', 'v2', 'v3'])
        self.assertEqual(sd.read(), '101112')
        sd = SegmentDump(client, ['v2', 'v3'])
        self.assertEqual(sd.read(), '1112')
        sd = SegmentDump(client, ['v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7', 'v8', 'v9'])
        self.assertEqual(sd.read(), '101112131415')

        # Segment Dumping w/ Params
        sd = SegmentDump(client, ['v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v8', 'v9'])
        self.assertEqual(sd.read(end_var_value='12'), '1011')
        self.assertEqual(sd.read(decode_data=True), 'abcdefgh')
        self.assertEqual(sd.read(decode_data=True, end_var_value='11'), 'a')
        self.assertEqual(sd.read(decode_data=True, end_var_value='f', encode_end=True), 'abcde')

    def test_get_segments(self):
        client = DummyClient(
            BaseCodec(force_lowercase=True).encode,
            BaseCodec(force_lowercase=True).decode,
            cloud_variables={'v1':'0', 'v2':'0', 'v3':'0', 'v4':'0', 'v5':'0', 'v6':'0', 'v7':'0', 'v8':'0', 'v9':'0'})
        
        sd = SegmentDump(client, ['v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7', 'v8', 'v9'])
        data = '0'*256 + '1'*256

        expected_data = {
            'v1':'0' * 256,
            'v2':'1' * 256,
            'v3':'0',
            'v4':'0',
            'v5':'0',
            'v6':'0',
            'v7':'0',
            'v8':'0',
            'v9':'0'
        }

        self.assertEqual(sd.get_segments(data), expected_data)

        expected_data = {
            'v1':'0' * 256,
            'v2':'1' * 256,
            'v3':'22',
            'v4':'22',
            'v5':'22',
            'v6':'22',
            'v7':'22',
            'v8':'22',
            'v9':'22'
        }

        self.assertEqual(sd.get_segments(data, empty_value='22'), expected_data)

        data = '0000' * 2560
        self.assertRaises(errors.SizeError, sd.get_segments, data)

        lorem_ipsum = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

        print(sd.get_segments(lorem_ipsum, encode_data = True))

        expected_data = {
            'v1': '2124271422461825283022461324212427462818294610221429544612242328141229142930274610131825182812182316461421182954462814134613244614183028222413462914222524274618231218131813302329463029462110112427144614294613242124271446221016231046102118263010554630294614',
            'v2': '2318224610134622182318224631142318102254462630182846232428292730134614331427121829102918242346302121102212244621101124271828462318281846302946102118263018254614334614104612242222241324461224232814263010295546133018284610302914461827302714461324212427461823',
            'v3': '4627142527141714231314271829461823463124213025291029144631142118294614282814461218212130224613242124271446143046153016181029462330212110462510271810293027554614331214252914302746281823294624121210141210294612302518131029102946232423462527241813142329544628',
            'v4': '30232946182346123021251046263018462415151812181046131428142730232946222421211829461023182246181346142829462110112427302255',
            'v5': '0', 'v6': '0', 'v7': '0', 'v8': '0', 'v9': '0'
        }

        self.assertEqual(sd.get_segments(lorem_ipsum, encode_data = True), expected_data)


if __name__ == '__main__':
    unittest.main()