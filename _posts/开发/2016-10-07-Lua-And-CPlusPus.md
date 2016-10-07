---
layout: post

title: Lua与C++交互及相互调用示例

category: 开发

tags: lua 

keywords: Linux lua C++ 

description: 本文介绍了lua和C++程序之间交互及相互调用的做法。

---

Lua作为一门发展成熟的脚本语言，正在变得越来越流行。它也可以作为和C/C++执行脚本交互的语言。并且Lua的整个库很小，很轻量，特别适合轻量级脚本嵌入。

Lua在和C/C++交互时，Lua运行环境维护着一份堆栈——不是传统意义上的堆栈，而是Lua模拟出来的。Lua与C/C++的数据传递都通过这份堆栈来完成，这份堆栈的代表就是lua_State*所指的那个结构。

堆栈通过lua_push系列函数向堆栈中压入值，通过luaL_check系列从堆栈中获取值。而用luaL_check系列函数时传递的参数索引。

其中，参数在栈中的索引为参数从左到右的索引（从1开始），栈顶元素索引也可以从-1记起。栈中元素个数可以用lua_gettop来获得，如果lua_gettop返回0，表示此栈为空。

本文主要通过代码实现lua与C/C++进行交互的各种场景：   

1. C++ 调用lua脚本
2. lua调用C++实现的动态库接口
3. C++程序调用lua脚本，再从lua中反调用C++程序中的函数

## 1. 简单测试
hello_world.cpp代码：  
		
		#include <stdio.h>
		
		//lua头文件
		#ifdef __cplusplus 
		extern "C"
		{
		#endif
		    #include <lua.h>
		    #include <lualib.h>
		    #include <lauxlib.h>
		#ifdef __cplusplus 
		}
		#endif
		
		int main()
		{
		    lua_State * state = luaL_newstate();
		    luaL_openlibs(state);
		    luaL_dostring(state, "print(\"hello lua, by cpp\")");
		    lua_close(state);
		}
编译、运行：  

	# g++ -o hello_world hello_world.cpp -llua
	# ./hello_world
	hello lua, by cpp

通过这个小例子就验证说明C++是可以调用lua的。接下来我们逐个验证lua与C++交互的几种情况。

## 2. C++ 调用lua脚本
目标：通过lua脚本生成一个xml文件。  

说明：  

1. 获取lua中的函数  

	lua_getglobal(L, hello);   // 假设该lua接口为 hello
2. 通过lua_push系列函数将C/C++数据类型的值压栈，即接口的输入参数
	
	int i = 33;
	float d = 1.234;
	std::string s("hello");
	lua_pushinteger(L, i);
	lua_pushnumber(L, d);
	lua_pushstring(s.c_str());
3. 执行

	lua_pcall(L, 3, 2, 0);   // lua 接口接收三个输入参数，且有2个返回值

generateXml.cpp代码：  
	
	#include <iostream>
	#include <string>
	
	extern "C"
	{
	#include <lua.h>
	#include <lualib.h>
	#include <lauxlib.h>
	//#pragma comment(lib, "lua.lib")
	};
	
	using namespace std;
	
	lua_State* initLuaEnv()
	{
		lua_State* luaEnv = lua_open();
		luaopen_base(luaEnv);
		luaL_openlibs(luaEnv);
		return luaEnv;
	}
	
	// 加载Lua文件到Lua运行时环境中.
	bool loadLuaFile(lua_State* luaEnv, const string& fileName)
	{
		int result = luaL_loadfile(luaEnv, fileName.c_str());
		if (result)
		{
			return false;
		}
		
		result = lua_pcall(luaEnv, 0, 0, 0);
		return result == 0;
	}
	
	// 获取全局函数.
	lua_CFunction getGlobalProc(lua_State* luaEnv, const string& procName)
	{
		lua_getglobal(luaEnv, procName.c_str());
		if (!lua_iscfunction(luaEnv, 1))
		{
			return 0;
		}
	
		return lua_tocfunction(luaEnv, 1);
	}
	
	int main()
	{
		// 初始化Lua运行时环境.
		lua_State* luaEnv = initLuaEnv();
		if (!luaEnv)
		{
			return -1;
		}
	
		// 加载脚本到Lua环境中.
		if (!loadLuaFile(luaEnv, "generateXML.lua"))
		{
			cout<<"Load Lua File FAILED!"<<endl;
			return -1;
		}
	
		// 获取信息.
		string fromName("beijing");
		string toName("shanghai");
		string msgContent("how many miles from these tow cities?");
	
		// 将要调用的函数和函数调用参数入栈.
		lua_getglobal(luaEnv, "generateNoteXML");
		lua_pushstring(luaEnv, fromName.c_str());
		lua_pushstring(luaEnv, toName.c_str());
		lua_pushstring(luaEnv, msgContent.c_str());
	
		// 调用Lua函数（3个参数,一个返回值）.
		lua_pcall(luaEnv, 3, 1, 0);
	
		// 获取返回值.
		if (lua_isboolean(luaEnv, -1))
		{
			int success = lua_toboolean(luaEnv, -1);
			if (success)
			{
				cout<<"\nGenerate Note File Successful!"<<endl;
			}
		}
	
		// 将返回值出栈.
		lua_pop(luaEnv, 1);
	
		// 释放Lua运行时环境.
		lua_close(luaEnv);
	
		return 0;
	}

generateXml.lua代码：  
	
	xmlHead = '<?xml version="1.0" encoding="utf-8" ?>\n'
	
	-- Open note file to wriet.
	function openNoteFile(fileName)
		return io.open(fileName, "w")
	end
	
	
	-- Close writed note file.
	function closeNoteFile(noteFile)
		noteFile:close()
	end
	
	function writeNestedLabel(ioChanel, label, nestCnt)
		if nestCnt == 0 then
			ioChanel:write(label)
			return
		end
	
		for i = 1, nestCnt do
			ioChanel:write("\t")
		end
	
		ioChanel:write(label)
	end
	
	function generateNoteXML(fromName, toName, msgContent)
		local noteFile = openNoteFile(fromName .. "_" .. toName .. ".xml")
		if not noteFile then
			return false
		end
	
		noteFile:write(xmlHead)
		noteFile:write("<note>\n")
	
		local currNestCnt = 1
		writeNestedLabel(noteFile, "<fromName>", currNestCnt)
		noteFile:write(fromName)
		writeNestedLabel(noteFile, "</fromName>\n", 0)
	
		writeNestedLabel(noteFile, "<toName>", currNestCnt)
		noteFile:write(toName)
		writeNestedLabel(noteFile, "</toName>\n", 0)
	
		local sendTime = os.time()
		writeNestedLabel(noteFile, "<sendTime>", currNestCnt)
		noteFile:write(sendTime)
		writeNestedLabel(noteFile, "</sendTime>\n", 0)
	
		writeNestedLabel(noteFile, "<msgContent>", currNestCnt)
		noteFile:write(msgContent)
		writeNestedLabel(noteFile, "</msgContent>\n", 0)
	
		noteFile:write("</note>\n")
		closeNoteFile(noteFile)
	
		return true
	end

编译、运行：  	
	
	# g++ -o generateXml generateXml.cpp -llua
	# ./generateXml
	
	Generate Note File Successful!
	# cat beijing_shanghai.xml
	<?xml version="1.0" encoding="utf-8" ?>
	<note>
	        <fromName>beijing</fromName>
	        <toName>shanghai</toName>
	        <sendTime>1472118014</sendTime>
	        <msgContent>how many miles from these tow cities?</msgContent>
	</note>

## 3. lua调用c++实现的动态库接口
目标：c++实现一个动态库，然后lua调用该动态库中的接口。  

说明：  

1. 所有要被lua调用c/c++函数都必须满足以下函数签名：

		typedef int (*lua_CFunction) (lua_State *L);
也就是说所有的函数必须接收一个lua_State作为参数，同时返回一个整数值。因为这个函数使用lua栈作为参数，所以它可以从栈里面读取任意数量和任意类型的参数。而这个函数的返回值则表示函数返回时有多少返回值被压入Lua栈。

2. 注册c/c++函数到lua运行时环境  
	
		lua_register(L, "hello", hello);   // 假设该c/c++函数原型是int hello(int, float)，而在lua中调用时使用的名字也叫hello
		或者使用下面的方式：  
		lua_pushcfunction(L, hello);
	    lua_setglobal(L, "hello");
		或者使用下面的方式（有多个c/c++函数需要注册时该办法最方便）：  
		static const luaL_Reg mylibs[]=
		{
		    {"hello", hello},
		    {NULL, NULL}
		};
		luaL_register(luaEnv, "libHelloCpp", luaLibs);  // 第二个参数相当于包名

	注意：动态库入口函数名必须是luaopen_{动态库文件名,除去后缀.so}，即假设你的动态库名字叫做libHello.so，那么：  
	
		extern "C" int luaopen_libgenerateCppSo(lua_State* luaEnv)  // 必须
		{  
		    const char* LIBRARY_NAME = "libHelloCpp"; // 此名字即是lua中调用时的包名, 可以和动态库文件名不一致
			lua_register(luaEnv, "hello", hello);
		    return 1;  
		}  

3. 在lua中调用   

		libHelloCpp.hello(12, 324.56)

generateCppSo.cpp 代码：  
		
	#include <stdio.h>
	#include <string>
	#ifdef __cplusplus 
	extern "C"
	{
	#endif
	    #include <lua.h>
	    #include <lualib.h>
	    #include <lauxlib.h>
	#ifdef __cplusplus 
	}
	#endif
	
	// 发生错误时报告错误.  
	void reportError(lua_State* luaEnv, const char* msg)  
	{  
	    lua_pushstring(luaEnv, msg);  
	    lua_error(luaEnv);  
	}  
	
	// 检测函数调用参数个数是否正常
	void checkArgsCount(lua_State* luaEnv, int paramCount)
	{
	    // lua_gettop获取栈中元素个数.  
	    if (lua_gettop(luaEnv) != paramCount)  
	    {  
	        reportError(luaEnv, "error : num of args");  
	    }  
	}
	
	#ifdef __cplusplus 
	extern "C"
	#endif
	int cpp_mul(lua_State *l)
	{
	    checkArgsCount(l, 2);
	
	    int a = lua_tointeger(l, 1);
	    int b = lua_tointeger(l, 2);
	    lua_pushinteger(l, a * b);
	    return 1;    // 返回值个数为1个
	} 
	
	#ifdef __cplusplus 
	extern "C"
	#endif
	int cpp_cat(lua_State *l)
	{
	    checkArgsCount(l, 2);
	
	    std::string a = lua_tostring(l, 1);
	    std::string b = lua_tostring(l, 2);
	    std::string r(a + "_" + b);
	    lua_pushstring(l, r.c_str());
	    return 1;    // 返回值个数为1个
	} 
	
	
	#ifdef __cplusplus 
	extern "C"
	#endif
	int cpp_print_int_string_float(lua_State *l)
	{
	    checkArgsCount(l, 3);
	
	    int a = lua_tointeger(l, 1);
	    std::string b = lua_tostring(l, 2);
	    float c = lua_tonumber(l, 3);
	
	    printf("cpp_print_int_string_float : %d %s %f\n", a, b.c_str(), c);
	    //lua_pushstring(l, a + "_" + b);
	    return 0;    // 返回值个数为0个
	} 
	
	
	// 导出函数列表.  
	static luaL_Reg luaLibs[] =  
	{  
	    {"cpp_mul", cpp_mul},  
	    {"cpp_cat", cpp_cat},  
	    {"cpp_print_int_string_float", cpp_print_int_string_float},  
	    {NULL, NULL}  
	};  
	  
	// 动态库入口函数，lua调用此入口函数. 入口函数名必须是luaopen_{动态库文件名,除去后缀.so}
	extern "C" 
	int luaopen_libgenerateCppSo(lua_State* luaEnv)  
	{  
	    const char* LIBRARY_NAME = "libgenerateCppSo";  // 此名字即是lua中调用时的包名
	    luaL_register(luaEnv, LIBRARY_NAME, luaLibs);  
		//lua_register(luaEnv, "cpp_mul", cpp_mul);
	  
	    return 1;  
	}  

callCppSo.lua 代码：  
	
	require "libgenerateCppSo"
	
	for k, v in pairs(libgenerateCppSo)
	    do 
	        print(k, v)
	    end
	--	cpp_cat function: 0x11fcd90
	--	cpp_mul function: 0x11fcd30
	--	cpp_print_int_string_float      function: 0x11fcdf0
	
	
	print(libgenerateCppSo.cpp_cat(2, 32))  -- 2_32
	print(libgenerateCppSo.cpp_mul(2, 3))   -- 6
	print(libgenerateCppSo.cpp_mul(2, 6))   -- 12
	print(libgenerateCppSo.cpp_cat(2, 456)) -- 2_456
	
	print(libgenerateCppSo.cpp_cat("2", "rty456$%")) -- 2_rty456$%
		
	print(libgenerateCppSo.cpp_print_int_string_float(5, "hello_world", 3.4567))
	-- cpp_print_int_string_float : 5 hello_world 3.456700	
	
	-- print(libgenerateCppSo.cpp_cat(2, 45b6))   -- stdin:1: malformed number near '45b6'
	--print(libgenerateCppSo.cpp_cat(2, "45b6")) -- 2_45b6

编译动态库、运行lua：  

	# g++ -o libgenerateCppSo.so -shared -fPIC generateCppSo.cpp
	# lua callCppSo.lua
	cpp_cat function: 0x24af0c0
	cpp_mul function: 0x24af090
	cpp_print_int_string_float      function: 0x24af0f0
	2_32
	6
	12
	2_456
	2_rty456$%
	cpp_print_int_string_float : 5 hello_world 3.456700

通过lua交互式进行调用：

![](http://i.imgur.com/dP7kgNL.png)  

其中：  

1. `require "libgenerateCppSo"` 是请求载入该动态库
2. 函数调用方式都是“包名.函数名”，而包名就是动态库的名字
3. `for k, v in pairs(libgenerateCppSo) do print(k, v) end` 可以用来查看一个包中的所有函数

## 4. C++程序调用lua脚本，再从lua中反调用C++程序中的函数
标题有点拗口，其实目标很简单。  
目标：一个C++主程序，调用lua中的lua函数，再从lua中调用C++主程序中的C函数。  

说明(和上面介绍lua调用动态库接口的做法大部分是一样的)：  

1. 所有要被lua调用c/c++函数都必须满足以下函数签名：

		typedef int (*lua_CFunction) (lua_State *L);

2. 注册c/c++函数到lua运行时环境（不再需要定义动态库入口函数）  
	
		lua_register(L, "hello", hello);   // 假设该c/c++函数原型是int hello(int, float)，而在lua中调用时使用的名字也叫hello
		或者使用下面的方式：  
		lua_pushcfunction(L, hello);
	    lua_setglobal(L, "hello");
		或者使用下面的方式（有多个c/c++函数需要注册时该办法最方便）：  
		static const luaL_Reg mylibs[]=
		{
		    {"hello", hello},
		    {NULL, NULL}
		};
		luaL_register(luaEnv, "libHelloCpp", luaLibs);  // 第二个参数相当于包名

3. 在lua中调用   

		libHelloCpp.hello(12, 324.56)

cppmain.cpp代码：  
	
	#include <stdio.h>
	#include <stdlib.h>
	#include <string.h>
	#include <errno.h>
	#include <stdarg.h>
	#include <string>
	
	//lua头文件
	#ifdef __cplusplus 
	extern "C"
	{
	#endif
	    #include <lua.h>
	    #include <lualib.h>
	    #include <lauxlib.h>
	#ifdef __cplusplus 
	}
	#endif
	
	#define err_exit(num,fmt, ...)  \
	    do{ printf("[%s:%d]" fmt "\n", __FILE__, __LINE__, ##__VA_ARGS__); return (num); } while(0)
	
	// lua中调用的c函数定义,实现乘法和减法
	// lua 调用C接口时，其每一个接口都是此形式，而具体的参数lua_pushXXX和lua_toXXX进行传递；luaState*所指的结构中包含了Lua调用此Dll时必备的Lua环境
	extern "C" int cmul_sub(lua_State *l) 
	{
	    int a = lua_tointeger(l, 1);    // 如果传进来的是浮点，会截断，如果传进来的是字符串，会按整数0处理
	    int b = lua_tointeger(l, 2);
	    printf("cmul_sub get params: %d, %d\n", a, b);
	    lua_pushinteger(l, a * b);
	    lua_pushinteger(l, a - b);
	    return 2;   // 返回值有2个
	}
	
	// lua中调用的c函数定义,实现字符串拼接
	extern "C" int ccat(lua_State *l) 
	{
	    std::string a = lua_tostring(l, 1);
	    const char* b = lua_tostring(l, 2);
	    const char* c = lua_tostring(l, 3);
	    a = a + "_" + b + "_" + c;
	    lua_pushstring(l, a.c_str());
	    return 1;   // 返回值只有一个
	}
	
	int main(int argc, char **argv)
	{
	    // step 1
	    lua_State *lua = luaL_newstate();       //创建lua运行环境
	    if(lua == NULL) err_exit(-1, "luaL_newstat() failed");
	
	    int ret = 0;
	
	    // step 2
	    ret = luaL_loadfile(lua, "subfunc.lua");   //加载lua脚本文件
	    if(ret != 0) err_exit(-1, "luaL_loadfile failed");
	    ret = lua_pcall(lua, 0, 0, 0) ;
	    if(ret != 0) err_exit(-1, "lua_pcall failed:%s", lua_tostring(lua, -1));
	
	
	    // 将本程序定义的几个接口注册给lua运行时环境
	    lua_pushcfunction(lua, cmul_sub);           //将C语言定义的cmul_sub函数注册到lua中, 以在lua中使用
	    lua_setglobal(lua, "cmul_sub");             //绑定到lua中的名字cmul_sub
	
	    lua_pushcfunction(lua, ccat);               //将C语言定义的ccat函数注册到lua中, 以在lua中使用
	    lua_setglobal(lua, "ccat");                 //绑定到lua中的名字ccat
	
	    {   // test cmul_sub
	        int a = 10, b = 3;
	        lua_getglobal(lua, "luamul_sub");       //调用lua中的luamul_sub函数，该函数调用本程序中定义的cmul函数实现乘法和减法
	        lua_pushinteger(lua, a);
	        lua_pushinteger(lua, b);
	        ret = lua_pcall(lua, 2, 2, 0);          // 2个参数，2个返回值
	        if(ret != 0) err_exit(-1, "lua_pcall failed:%s, %s", lua_tostring(lua, -1), lua_tostring(lua, -2));
	        // -1 及N(返回值个数) 表示栈顶; -N(返回值个数) 及 1 表示栈底
	        printf("luamul_sub: %d * %d = %ld, %d - %d = %d\n\n", a, b, lua_tointeger(lua, -2), a, b, lua_tointeger(lua, -1));
	        printf("luamul_sub: %d * %d = %ld, %d - %d = %d\n\n", a, b, lua_tointeger(lua, 1), a, b, lua_tointeger(lua, 2));
	        lua_pop(lua, 2);   // 2 个返回值，所以栈要弹出2次
	    }
	    {   // test cmul_sub : 测试传递浮点数和字符串值并进行乘法和减法运算
	        float d1 = 12.34;
	        const char* d2 = "hello";
	        lua_getglobal(lua, "luamul_sub");       //调用lua中的luamul_sub函数，该函数调用本程序中定义的cmul函数实现乘法和减法
	        lua_pushnumber(lua, d1);
	        lua_pushstring(lua, d2);
	        ret = lua_pcall(lua, 2, 2, 0);          // 2个参数，2个返回值
	        if(ret != 0) err_exit(-1, "lua_pcall failed:%s, %s", lua_tostring(lua, -1), lua_tostring(lua, -2));
	        // -1 及N(返回值个数) 表示栈顶; -N(返回值个数) 及 1 表示栈底
	        printf("luamul_sub: %f * %s = %ld, %f - %s = %d\n\n", d1, d2, lua_tointeger(lua, -2), d1, d2, lua_tointeger(lua, -1));
	        lua_pop(lua, 2);   // 2 个返回值，所以栈要弹出2次
	    }
	
	    {   // test ccat
	        int a = 111, b = 232;
	        lua_getglobal(lua, "luacat");           //调用lua中的luacat函数，该函数调用本程序中定义的ccat函数实现字符串拼接
	        lua_pushinteger(lua, a);
	        lua_pushinteger(lua, b);
	        lua_pushinteger(lua, 1234);
	        ret = lua_pcall(lua, 3, 1, 0);          // 3个参数，1个返回值
	        if(ret != 0) err_exit(-1, "lua_pcall failed:%s", lua_tostring(lua, -1));
	        printf("luacat: %d, %d, %d = %s\n\n", a, b, 1234, lua_tostring(lua, 1));
	        lua_pop(lua, 1);                        // 1 个返回值，所以栈要弹出1次
	    }
	    {   // test ccat : 测试压入不同类型的数据然后进行拼接: 字符串、浮点型、整形
	        const char* c1 = "hello"; 
	        float c2 = 12.5678; 
	        int c3 = 123456; 
	        lua_getglobal(lua, "luacat");           //调用lua中的luacat函数，该函数调用本程序中定义的ccat函数实现字符串拼接
	        lua_pushstring(lua, c1);
	        lua_pushnumber(lua, c2);
	        lua_pushinteger(lua, c3);
	        ret = lua_pcall(lua, 3, 1, 0);          // 3个参数，1个返回值
	        if(ret != 0) err_exit(-1, "lua_pcall failed:%s", lua_tostring(lua, -1));
	        printf("luacat: %s, %f, %d = %s\n\n", c1, c2, c3, lua_tostring(lua, 1));
	        lua_pop(lua, 1);                        // 1 个返回值，所以栈要弹出1次
	    }    
	
	    // step 3
	    lua_close(lua);                         //释放lua运行环境
	    return 0;
	}

subfunc.lua代码：  
	
	--lua函数定义，通过调用c代码中的cmul函数实现乘法和减法
	function luamul_sub(a, b)
	    return cmul_sub(a, b);
	end
	
	--lua函数定义，通过调用c代码中的ccat函数实现字符串连接
	function luacat(a, b, c)
	    c = c .. "__modifyByLua"  -- 模拟在lua中先对输入进行处理
	    return ccat(a, b, c);
	end

编译、运行：  
	
	# g++ -o cppmain cppmain.cpp -llua
	# ./cppmain
	cmul_sub get params: 10, 3
	luamul_sub: 10 * 3 = 30, 10 - 3 = 7
	
	luamul_sub: 10 * 3 = 30, 10 - 3 = 7
	
	cmul_sub get params: 12, 0
	luamul_sub: 12.340000 * hello = 0, 12.340000 - hello = 12
	
	luacat: 111, 232, 1234 = 111_232_1234__modifyByLua
	
	luacat: hello, 12.567800, 123456 = hello_12.567799568176_123456__modifyByLua
