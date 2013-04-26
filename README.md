EnumGen
=======

This is a small python script to generate enhanced C++ enums. The original author of this script is [Rico Huijbers](https://github.com/rix0rrr). The script was published with permission of the copyright holder, [Sioux Embedded Systems](http://www.sioux.eu/en/), and is released under the MIT license.

Background
==========

C++ enums are not very programmer-friendly. One problem is that the syntax for enum values does not include the enum type, which can lead to naming conflicts and is not very readable. Another issue is that there is no standard way to convert to and from string representations of the enum values, which is often handy for logging and testing purposes. While C++11 has slightly improved on this, it does not go far enough. For this reason, we came up with an enhanced version of the basic C++ enum, of the following form:

    namespace Color
    {
        enum Enum
        {
                RED,
                GREEN,
                BLUE,
                YELLOW,
                _Count
        };
        std::vector<Enum> values();
        std::string name(Enum e);
        Enum valueOf(std::string str);
    }
    std::ostream& operator<<(std::ostream& os, const Color::Enum& e);

This has a few nice properties:

* An enum value must include the name of the Enum, e.g. Color::RED
* The function "values()" returns a vector containing all valid values for the enum, which can be used for iteration purposes, e.g. using boost's foreach
* The functions name(Enum) and valueOf(std::string) can be used to convert to and from string representations of the enum values
* The function operator<< is handy when using streams to write to console or a file, e.g. std::cout << "Current color is " << color; // Where color is of type Color::Enum

The only significant disadvantage is that you have to declare a variable as being of type Color::Enum.

However, writing the underlying code for each enum in a project is tedious and error-prone. The EnumGen script alleviates this by letting you specify enums in a concise way, and generating a .h and .cpp file containing the proper definition and implementation.

Specifying enums
================

Take a look at example.py to see how enums are specified. In short, to specify an enum you write a python script in which you call enumgen.define with a pathname, enum type name and a list of string pairs. The list of string pairs contains all the enum values. The first element of each pair is the actual name of the value, the second element is the string version of the same value. So

    enumgen.define('colorapp', 'Color', [('RED' , 'Red'),('GREEN' , 'Green')])

is the specification for an enum named Color, with values Color::RED and Color::Green. Calling Color::name(RED) will return the string "Red". The files will be placed in a directory named "colorapp".

For larger enum specifications, it is far more readable to spread out the spec over multiple lines as follows

    enumgen.define('colorapp', 'Color', [
            ('RED'    , 'Red'),
            ('GREEN'  , 'Green'),
        ])

Using the generator
===================

In the enum specification python script, the final step after the calls to enumgen.define is a call to enumgen.write. This function accepts two strings as parameters: The root directory in which all enums will be placed, and the name of the specification script itself. The latter is included only for documentation purposes. 

To generate the C++ code, simply execute the specification python script, for example as follows:

    python example.py
