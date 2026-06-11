#define S 1024

static int FP(int x, int g) {
	if (x <= 0)return 0;
	if (x >= S)return S;
	long t = x - S;
	long ln = t * (S - (x >> 1) + x * x / (3 * S)) / S;
	long lg = ln * g / S;
	long ex = S + lg + lg * lg / (2 * S);
	return ex < 0 ? 0 : (ex > S ? S : ex);
}


int T1(const char* id, int g, const int* lv, const int* reg, int* o) {
	static const unsigned char G[30] = { 255,254,252,250,248,246,244,242,240,232,224,208,192,160,128,127,95,63,47,31,23,15,13,11,9,7,5,3,1,0 };
	int T[30], O[30], L[30], R = lv[0] - lv[29];
	O[0] = reg[0]; O[29] = reg[29];
	for (int k = 0; k < 30; k++)L[k] = lv[k];
	T[0] = L[0]; T[29] = L[29];
	for (int i = 1; i < 29; i++)T[i] = (int)((long)FP((int)((long)G[i] * S / 255), g) * R / S + L[29]);
	for (int i = 1; i < 29; i++)for (int j = 0; j < 29; j++)if (T[i] <= L[j] && T[i] >= L[j + 1]) { int d = reg[j] - reg[j + 1]; if (d) { O[i] = (int)((long)(T[i] - L[j + 1]) * d / (L[j] - L[j + 1]) + reg[j + 1]); if (O[i] < 1)O[i] = 1; if (O[i] > 1023)O[i] = 1023; }break; }
	for (int i = 0; i < 29; i++) { if (O[i] < 1)O[i] = 1; if (O[i] > 1023)O[i] = 1023; if (O[i] < G[i])O[i] = G[i]; }
	for (int i = 0; i < 28; i++)if (O[i] <= O[i + 1])O[i] = O[i + 1] + G[i] - G[i + 1];
	for (int i = 0; i < 30; i++)o[i] = O[i];
	return 0;
}

typedef int(*MF)(int); typedef void(*WF)(int, int, int, int, unsigned char);

int T2(int i, int gy, int t, int c1, int c2, int c3, unsigned char sn, MF m, WF w, int* o1, int* o2, int* o3, unsigned char* os) {
	int p = i % 3, b = 0, d = 0x7FFFFFFF, mx = p == 0 ? 1 : (p == 1 ? 15 : 3);
	for (int k = 0; k <= mx; k++) {
		int a = p == 2 ? k : c1, bb = p == 1 ? k : c2, cc = p == 0 ? (k & 7) : c3, ss = p == 0 ? (k >> 3) : sn;
		if (w)w(i, a, bb, cc, ss);
		int lv = m ? m(gy) : 0, dd = lv > t ? lv - t : t - lv;
		if (dd < d) { d = dd; b = k; }
	}
	if (p == 0) { *os = b >> 3; *o3 = b & 7; *o1 = *o2 = 0; }
	else if (p == 1) { *os = sn; *o3 = c3; *o2 = b; *o1 = 0; }
	else { *os = sn; *o3 = c3; *o2 = c2; *o1 = b; }
	return 0;
}