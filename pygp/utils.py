import collections

def remove_space(bytestring):
    """
        Removes all whitespace characters of a string.

        :param str bytestring: The string to manage

        :returns: str bytestr: the string without whitepace characters

    """
    import re
    bytestring = ''.join( re.split( '\W+', bytestring.upper() ) )
    return bytestring

def toByteArray(byteString):
    """
        Returns a list of bytes from a byte string
        
        :param str bytestring: a hexadecimal string

        :returns: list list_byte: the list of bytes

        ::

            # get the list of bytes from the hexadecimal string
            astr = "3B65000  09C11 0101 03"
            toByteArray( astr ) # returns  [ 0x3B, 0x65, 0x00, 0x00, 0x9C, 0x11, 0x01, 0x01, 0x03 ]

        
    """
    import re
    packedstring = ''.join( re.split( '\W+', byteString.upper() ) )
    aArray = bytearray.fromhex(packedstring.upper())
    value = list(aArray)
    return value

def toHexString(bytes=[]):
    """
        Returns a hexadecimal string from a list of bytes
        
        :param list bytes: a list of bytes

        :returns: str bytestr: the hexadecimal string 

        ::

            # get the string from the list of bytes
            a_list = [ 0x3B, 0x65, 0x00, 0x00, 0x9C, 0x11, 0x01, 0x01, 0x03 ]
            toHexString( a_list ) # returns  "3B6500009C11010103"
        
    """
    value = ""
    for i in range (0, len(bytes)):
        if (bytes[i] < 0x00):
            return None
        value += ("%-0.2X" % bytes[i])
    return value


def getBytes(data, byteNumber,length = 1):
    """
        Returns the part of data string from byte number to length bytes
        
        :param str data: a hexadecimal string
        :param int byteNumber: the start offset into the string
        :param int length: The bytes length to get

        :returns: str bytestr: the hexadecimal string 

        ::

            # get the string from byte 2 with a length of 3
            astr = "3B65000  09C11 0101 03"
            getBytes(astr, 2, 3) # returns  "650000"
        
    """

    import re
    bytestr = ''.join( re.split( '\W+', data.upper() ) )
    byteArray = toByteArray(bytestr)
    part = byteArray[byteNumber - 1:byteNumber - 1 + length]
    return toHexString(part)

def lv(bytestring):
    '''
        Returns a byte String representing the length content preceding by its length.

        :param str bytestring: a hexadecimal string

        :returns: str bytestr: the hexadecimal string preceded by its length 
        
        .. note:: for byte string up to FF bytes, the length is coded with 2 bytes.

        ::

            # get the string preceded by its length
            astr = "3B65000  09C11 0101 03"
            lv(astr) # returns  "093B65000 09C11010103"
        

    '''
    import re
    bytestr = ''.join( re.split( '\W+', bytestring.upper() ) )

    length = int(len(bytestr)/2)
    if (length > 0xFF):
        #length on 2 bytes
        return intToHexString(length,2) + bytestr
    else:
        return intToHexString(length,1) + bytestr


def intToHexString(intValue, len = 1):
    """
        Returns a hexadecimal string representing an integer
        
        :param int intValue: an integer value
        :param int len: the number of byte expected for the string

        :returns: str bytestr: the hexadecimal string 


        ::

            # get the string representation of the integer
            aInt = 10
            intToHexString ( aInt, 2 ) #returns  "000A"
            

    """
    stringValue = hex(intValue).lstrip('0x')
    stringValue = stringValue.rjust(len*2,'0')
    return stringValue.upper()


def getLength(bytestr, len = 1):
    '''
        Returns a string representing the length of the string as parameter on numberOfBytes bytes

        :param str bytestr: a hexadecimal string
        :param int len: the number of byte expected for the string
        
        ::

            getLength("A0A40002", 2) # returns "0004"
            getLength("A0A40002", 1) # returns "02"

            
    '''
    import re
    bytestr = ''.join( re.split( '\W+', bytestr.upper() ) )
    length = int(len(bytestr)/2)
    return intToHexString(length,len)



def increment(bytestr,value):
    '''
        This function increments an hexadecimal string with the integer value.
        The value could be an integer or a string.
    
        :param str bytestr: a hexadecimal string
        :param int value: the value to increment


        ::

            aStr = '01'
            aInt = 0x03
            newStr = increment ( aStr, aInt ) # returns  "04"
            aInt = '03'
            newStr = increment ( aStr, aInt ) # returns  "04"


    '''
    import re
    data = ''.join( re.split( '\W+', bytestr.upper() ) )
    # value is an integer
    if type(value) is int:
        # addition
        data_value = int(data, 16)
        data_value = data_value + value
        tmp_string = intToHexString(data_value)
        # return value on the same length
        while len(tmp_string) < len(data) :
            tmp_string = '00' + tmp_string

    # value is a string
    elif type(value) is str:
        #remove space
        value = ''.join( re.split( '\W+', value.upper() ) )
        # addition
        data_value = int(data, 16)
        value = int(value, 16)
        data_value = data_value + value
        tmp_string = intToHexString(data_value)
        # return value on the same length
        while len(tmp_string) < len(data) or len(tmp_string) < len(value) :
            tmp_string = '00' + tmp_string

    else:
        raise BaseException("Wrong parameter type")

    return tmp_string


TAG_TYPE_PRIMITIVE = 0x0
TAG_TYPE_CONSTRUCTED = 0x1

TAG_SIZE_BIG_1 = 0x81
TAG_SIZE_BIG_2 = 0x82

def tlv_read(strResponse):
    if strResponse == None:
        return
    
    byte_list_data = toByteArray(strResponse)
    data_len = len(byte_list_data)
    i = 0
    tlv_dic = {}
    while i < data_len:
        # Exception case.
        # ECC CERT 7F49 <var> B0 <var> data, in this case, B0 is not contructed TLV tag
        # SCRS Get CRS status, Tag 7F99 contain Wallet name. 7F99 is not contruncted TLV tag
        if ((byte_list_data[i] == 0xB0) | \
           ((byte_list_data[i] == 0x7F) & (byte_list_data[i+1] == 0x99))):
           tag_type = TAG_TYPE_PRIMITIVE
        else:
            tag_type = (byte_list_data[i]&0b00100000)>>5    # Contructed or primitive

        # Get Tag
        if byte_list_data[i]&0b00011111 == 0b00011111:
            strTag = ("%-0.2X"%byte_list_data[i])
            strTag += ("%-0.2X"%byte_list_data[i+1])
            i += 2
        else:
            strTag = ("%-0.2X"%byte_list_data[i])
            i += 1

        # Get Length
        if byte_list_data[i] == TAG_SIZE_BIG_1:
            length = byte_list_data[i+1]
            i += 2
        elif byte_list_data[i] == TAG_SIZE_BIG_2:
            length = 256 * byte_list_data[i+1] + byte_list_data[i+2]
            i += 3
        else:
            length = byte_list_data[i]
            i += 1

        # Get Value, to avoid out of range problem check the length.
        if (i + length) > data_len:
            value = byte_list_data[i:i+data_len]
            #i += length
            #strValue = toHexString(value)
            print("ERROR???   " + toHexString(value))
        else:
            value = byte_list_data[i:i+length]
            i += length
            strValue = toHexString(value)

        if tag_type == TAG_TYPE_CONSTRUCTED and length == len(value) and length > 2:
            ret_dic = tlv_read(strValue)
            # print(strTag)
            if strTag in tlv_dic.keys():
                # Key already exist in dictionary.
                if type(tlv_dic[strTag]) == list:
                    # list already exist, then just append the value at list
                    tlv_dic[strTag].append(ret_dic)
                # So add new value as a list.
                else:
                    saveDic = tlv_dic[strTag]
                    tlv_dic[strTag] = [saveDic, ret_dic]
            else:        
                tlv_dic[strTag] = ret_dic
        else:
            # print(strTag + "  " + strValue)
            if strTag in tlv_dic.keys():
                # Key already exist in dictionary.
                if type(tlv_dic[strTag]) == list:
                    # list already exist, then just append the value at list
                    tlv_dic[strTag].append(strValue)
                # So add new value as a list.
                else:
                    prevValue = tlv_dic[strTag]
                    tlv_dic[strTag] = [prevValue, strValue]
            else:
                tlv_dic[strTag] = strValue

    return tlv_dic

def tlv_print(tlv_dic, indent = '  '):
    for tag, value in tlv_dic.items():
        if type(value) == dict:
            print(indent + tag)
            tlv_print(value, indent + '  ')
        elif type(value) == list:
            print(indent + tag)
            for items in tlv_dic[tag]:
                if type(items) == dict:
                    tlv_print(items, indent + indent)
                else:
                    print(indent + indent + items)
        elif type(value) == str:
            print(indent + tag + ' ' + value)
 