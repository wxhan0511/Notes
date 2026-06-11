#pragma once
#ifdef __cplusplus
extern "C" {
#endif

	typedef int (*MFn)(int gray);
	typedef void (*WFn)(int idx, int c1, int c2, int c3, unsigned char sn);

	int T1(const char* id, int gamma, const int* lv, const int* reg, int* out);

	int T2(int idx, int gray, int tgt, int c1, int c2, int c3, unsigned char sn, MFn m, WFn w, int* o1, int* o2, int* o3, unsigned char* os);

#ifdef __cplusplus
}
#endif