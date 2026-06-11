#pragma once
#ifdef __cplusplus
extern "C"{
#endif

#ifndef GAMMA_API_PLAINTEXT_NAMES
#define Tuning GammaTuning__f73a91b0
#define Tuning_Enhance GammaTuning__4c1d2e97
#endif

typedef int(*MF)(int);typedef void(*WF)(int,int,int,int,unsigned char);
int Tuning(const char*id,int g,const int*lv,const int*reg,int*o);
int Tuning_Enhance(int i,int gy,int t,int c1,int c2,int c3,unsigned char sn,MF m,WF w,int*o1,int*o2,int*o3,unsigned char*os);
#ifdef __cplusplus
}
#endif
