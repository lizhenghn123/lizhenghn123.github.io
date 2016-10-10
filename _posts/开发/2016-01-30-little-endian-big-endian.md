---
layout: post

title: 网络编程中的字节序问题

category: 开发

tags: 开发 网络

keywords: 开发 网络 字节序

description: 网络编程中的字节序问题， 关于大端法、小端法的判断， 网络字节序和主机字节序及相互转换。

---

在使用C/C++编写网络程序的时候，往往会遇到字节序的问题。字节序通常来说有主机字节序、网络字节序的区别，或者说是小端字节序（little endian）、大端字节序（big endian）。

- 小端法(Little-Endian)  
  就是低位字节排放在内存的低地址端即该值的起始地址，高位字节排放在内存的高地址端。
- 大端法(Big-Endian)  
  就是高位字节排放在内存的低地址端即该值的起始地址，低位字节排放在内存的高地址端。

怎么确定某一机器是大端还是小端呢，可以通过以下简单代码进行验证：

	bool isLittleEndian()
	{
	    //联合体union的存放顺序是所有成员都从低地址开始存放
	    union w
	    {
	        int i;
	        char c;
	    } u;
	    u.i = 1;
	
	    return (u.c == 1);
	}

不同的CPU架构有不同的字节序（和操作系统无关）， X86机器上一般是小端字节序，而网络编程中进行数据传输时是按字节流进行传输的，比如对于4个字节的32 bit值进行传输时，首先传输0～7bit，其次8～15bit，然后16～23bit，最后是24~31bit。这种即是大端法，也即网络字节序。

因此在网络编程中通常需要将要发送的数据先进行字节序转换。在Linux系统下有以下的API可以直接使用：

	NAME
	       htonl, htons, ntohl, ntohs - convert values between host and network byte order	
	SYNOPSIS
	       #include <arpa/inet.h>	
	       uint32_t htonl(uint32_t hostlong);	
	       uint16_t htons(uint16_t hostshort);	
	       uint32_t ntohl(uint32_t netlong);	
	       uint16_t ntohs(uint16_t netshort);	
	DESCRIPTION
	       The htonl() function converts the unsigned integer hostlong from host byte order to network byte order.	
	       The htons() function converts the unsigned short integer hostshort from host byte order to network byte order.	
	       The ntohl() function converts the unsigned integer netlong from network byte order to host byte order.	
	       The ntohs() function converts the unsigned short integer netshort from network byte order to host byte order.	
	       On the i386 the host byte order is Least Significant Byte first, whereas the network byte order, as used on the Internet, is Most Significant Byte first.


而在glibc中又增加了以下几个API(glibc2.9及以上)，用于主机字节序和小端/大端字节序的相互转换：

	NAME
	       htobe16, htole16, be16toh, le16toh, htobe32, htole32, be32toh, le32toh, htobe64, htole64, be64toh, le64toh - convert values between host and big-/little-endian byte order
	SYNOPSIS
	       #define _BSD_SOURCE
	       #include <endian.h>
	
	       uint16_t htobe16(uint16_t host_16bits);
	       uint16_t htole16(uint16_t host_16bits);
	       uint16_t be16toh(uint16_t big_endian_16bits);
	       uint16_t le16toh(uint16_t little_endian_16bits);
	
	       uint32_t htobe32(uint32_t host_32bits);
	       uint32_t htole32(uint32_t host_32bits);
	       uint32_t be32toh(uint32_t big_endian_32bits);
	       uint32_t le32toh(uint32_t little_endian_32bits);
	
	       uint64_t htobe64(uint64_t host_64bits);
	       uint64_t htole64(uint64_t host_64bits);
	       uint64_t be64toh(uint64_t big_endian_64bits);
	       uint64_t le64toh(uint64_t little_endian_64bits);
	
	DESCRIPTION
	       These functions convert the byte encoding of integer values from the byte order that the current CPU (the "host") uses, to and from little-endian and big-endian byte order.
	
	       The number, nn, in the name of each function indicates the size of integer handled by the function, either 16, 32, or 64 bits.
	
	       The functions with names of the form "htobenn" convert from host byte order to big-endian order.
	       The functions with names of the form "htolenn" convert from host byte order to little-endian order.
	       The functions with names of the form "benntoh" convert from big-endian order to host byte order.
	       The functions with names of the form "lenntoh" convert from little-endian order to host byte order.


以上介绍的接口都是Linux下的，Window系统上也有类似接口(肯定有htonl, htons, ntohl, ntohs)，但有没有htobe系列的接口我就不确定了。


对于如果是int64_t或者uint64_t类型，没有ntoh系列接口支持，也没有htobe64接口可以使用，就需要自己写一个转换程序了：
	
	uint64_t htonll(uint64_t v)
	{
	    union
	    {
	        uint32_t lv[2];
	        uint64_t llv;
	    } u;
	    u.lv[0] = htonl(v >> 32);
	    u.lv[1] = htonl(v & 0xFFFFFFFFULL);
	    return u.llv;
	}
	
	int64_t ntohll(uint64_t v)
	{
	    union
	    {
	        uint32_t lv[2];
	        uint64_t llv;
	    } u;
	    u.llv = v;
	    return ((uint64_t)ntohl(u.lv[0]) << 32) | (uint64_t)ntohl(u.lv[1]);
	}
