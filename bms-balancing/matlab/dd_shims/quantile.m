function q = quantile(x, p)
%QUANTILE  분위수 — **기본 MATLAB 만으로 구현한 대체품**.
%
%   ⚠ MathWorks 의 Statistics and Machine Learning Toolbox 함수가 아니다.
%     `dd_shims/` 를 경로에 넣었을 때만 쓰인다.
%
%   MATLAB 의 정의를 그대로 따른다: 정렬한 표본에 plotting position
%   (i-0.5)/n 을 주고 그 사이를 선형 보간, 양 끝은 최소·최대값으로 고정.
%   (numpy 기본값 (i-1)/(n-1) 과 다르다 — 이 차이가 창 자르기 경계를 몇 점씩
%   옮기므로 정의를 맞추는 것이 중요하다.)
%
%   규진팀 코드는 `quantile(vec, scalar)` 형태로만 쓴다. 그 경우만 지원한다.

    x = x(:);
    x = x(isfinite(x));
    x = sort(x);
    n = numel(x);

    if n == 0
        q = NaN;
        return
    end
    if n == 1
        q = x(1);
        return
    end
    if ~isscalar(p)
        error('quantile(shim): 스칼라 p 만 지원한다 (규진팀 코드가 쓰는 형태)');
    end

    pos = ((1:n)' - 0.5) / n;
    q = interp1(pos, x, p, 'linear');
    if p < pos(1),  q = x(1);   end
    if p > pos(end), q = x(end); end
end
