#include "GammaTuning.h"
#define TL(lv29,r,f) ((lv29)+((((((r)+8)>>4)*(int)(f))+1024)>>11))


int Tuning(const char* id, int g, const int* lv, const int* reg, int* o) {
	static const unsigned char G[30] = { 255,254,252,250,248,246,244,242,240,232,224,208,192,160,128,127,95,63,47,31,23,15,13,11,9,7,5,3,1,0 };
	static const unsigned short P[30] = { 32768,32486,31926,31371,30822,30277,29739,29205,28677,26616,24638,20932,17552,11752,7193,7070,3733,1512,794,318,165,64,47,33,21,12,6,2,0,0 };
	int O[30], r = lv[0] - lv[29];
	O[0] = reg[0]; O[29] = reg[29];
	for (int i = 1; i < 29; i++) {
		int t = TL(lv[29], r, P[i]);
		for (int j = 0; j < 29; j++)if (t <= lv[j] && t >= lv[j + 1]) { int d = reg[j] - reg[j + 1]; if (d) { O[i] = (int)((long)(t - lv[j + 1]) * d / (lv[j] - lv[j + 1]) + reg[j + 1]); if (O[i] < 1)O[i] = 1; if (O[i] > 1023)O[i] = 1023; }break; }
	}
	for (int i = 0; i < 29; i++) { if (O[i] < 1)O[i] = 1; if (O[i] > 1023)O[i] = 1023; if (O[i] < G[i])O[i] = G[i]; }
	for (int i = 0; i < 28; i++)if (O[i] <= O[i + 1])O[i] = O[i + 1] + G[i] - G[i + 1];
	for (int i = 0; i < 30; i++)o[i] = O[i];
	return 0;
}

int Tuning_Enhance(int i, int gy, int t, int c1, int c2, int c3, unsigned char sn, MF m, WF w, int* o1, int* o2, int* o3, unsigned char* os) {
	int p = i % 3, b = 0, d = 0x7FFFFFFF, mx = p == 0 ? 15 : (p == 1 ? 15 : 3), inc = 0, last = 0x7FFFFFFF;
	for (int k = 0; k <= mx; k++) {
		int a = p == 2 ? k : c1, bb = p == 1 ? k : c2, cc = p == 0 ? (k & 7) : c3, ss = p == 0 ? ((k >> 3) & 1) : sn;
		if (w)w(i, a, bb, cc, ss);
		int lv = m ? m(gy) : 0, dd = lv > t ? lv - t : t - lv;
		if (dd < d) { d = dd; b = k; inc = 0; }
		if (p && k > b && dd > last) { if (++inc > 1)break; }
		else inc = 0;
		last = dd;
	}
	if (p == 0) { *os = (b >> 3) & 1; *o3 = b & 7; *o1 = *o2 = 0; }
	else if (p == 1) { *os = sn; *o3 = c3; *o2 = b; *o1 = 0; }
	else { *os = sn; *o3 = c3; *o2 = c2; *o1 = b; }
	return 0;
}