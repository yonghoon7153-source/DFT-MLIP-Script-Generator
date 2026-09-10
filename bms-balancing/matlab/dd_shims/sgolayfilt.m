function y = sgolayfilt(x, order, framelen)
%SGOLAYFILT  Savitzky-Golay 평활 — **기본 MATLAB 만으로 구현한 대체품**.
%
%   ⚠ 이것은 MathWorks 의 Signal Processing Toolbox 함수가 아니다.
%     `dd_shims/` 를 경로에 넣었을 때만 쓰인다 (addpath 로 명시적으로).
%     그러므로 이 파일로 계산한 값은 "MATLAB 의 답" 이 아니라
%     **"우리 구현의 답"** 이다. 대조표에 그렇게 적을 것.
%
%   왜 만드나: 툴박스가 없는 기계에서 규진팀 코드(`differential.m` ·
%   `electrode_balancing_blend.m`)를 **고치지 않고** 돌리기 위해서다.
%   MATLAB 이 현재 폴더/경로를 먼저 보므로, 그들 코드는 이 파일을 부른다.
%
%   구현은 MATLAB 문서가 적은 sgolayfilt 의 정의 그대로다:
%     · 창 길이 f = 2m+1, 차수 order 의 다항 최소제곱 사영행렬
%           p = (-m:m)',  V = p.^(0:order),  H = V*((V'V)\V')
%     · 정상 구간: H 의 가운데 행을 FIR 로 쓴다 (각 샘플을 중심으로)
%     · 양 끝 전이 구간: 첫 f 개(마지막 f 개)에 H 의 해당 행을 곱한다
%
%   scipy 의 `savgol_filter(..., mode='interp')` 가 같은 방침이다 — 이
%   파일은 Python 포팅과 MATLAB 사이의 그 자리를 **직접 비교 가능**하게 만든다.

    x = x(:);
    n = numel(x);

    if mod(framelen, 2) == 0
        error('sgolayfilt(shim): framelen 은 홀수여야 한다 (받은 값 %d)', framelen);
    end
    if framelen > n
        error('sgolayfilt(shim): framelen %d 이 데이터 길이 %d 보다 크다', framelen, n);
    end
    if order >= framelen
        error('sgolayfilt(shim): order(%d) 는 framelen(%d) 보다 작아야 한다', order, framelen);
    end

    m = (framelen - 1) / 2;
    p = (-m:m)';
    V = p .^ (0:order);            % Vandermonde (framelen x order+1)
    H = V * ((V' * V) \ V');       % 사영행렬 (framelen x framelen)

    y = zeros(n, 1);

    % ── 정상 구간: 가운데 행을 FIR 계수로 ──
    c = H(m+1, :);                 % 길이 framelen
    for k = (m+1):(n-m)
        y(k) = c * x(k-m : k+m);
    end

    % ── 앞쪽 전이 구간 ──
    head = x(1:framelen);
    for k = 1:m
        y(k) = H(k, :) * head;
    end

    % ── 뒤쪽 전이 구간 ──
    tail = x(n-framelen+1 : n);
    for k = 1:m
        y(n-m+k) = H(m+1+k, :) * tail;
    end
end
