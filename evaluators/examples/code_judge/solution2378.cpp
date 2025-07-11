#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int N, M;
    if (!(cin >> N >> M)) return 0;

    vector<int> a(N), b(N);
    for (int i = 0; i < N; ++i) cin >> a[i] >> b[i];

    while (M--) {
        int c, d;
        cin >> c >> d;

        int best = 0, cur = 0;
        for (int i = 0; i < N; ++i) {
            if (a[i] <= d && b[i] >= c) {   // intervals overlap
                if (++cur > best) best = cur;
            } else {
                cur = 0;
            }
        }
        cout << best << '\n';
    }
    return 0;
}