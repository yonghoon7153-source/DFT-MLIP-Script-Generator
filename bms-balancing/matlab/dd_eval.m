function dd_eval(varargin)
%DD_EVAL  **적합 없이** 목적함수만 평가한다 — 툴박스 없는 기계용 포팅 대조.
%
%   왜 이것이 필요한가
%   ------------------
%   `dd_verify('dump')` 는 `fmincon`+`MultiStart` 가 있어야 돈다. 툴박스가
%   없으면 적합을 못 한다. 그런데 **포팅 대조에 정말 필요한 것은 적합이
%   아니라 모델이다.** 같은 파라미터 p 에서 MATLAB 과 Python 이 같은
%   RMSE 를 내는지가 핵심이고, 그건 최적화기 없이 잴 수 있다.
%
%   이 파일이 쓰는 것: `electrode_ocv` · `differential` ·
%   `build_blend_functions` (전부 규진팀 원본) + `dd_shims/` 의 대체 함수 둘
%   (`sgolayfilt` · `quantile`). 최적화기는 안 쓴다.
%
%   ⚠ `dd_shims/` 는 MathWorks 구현이 아니다. 그러므로 여기서 나온 값은
%     "MATLAB 의 답" 이 아니라 **"규진팀 모델 + 우리 대체 함수"** 의 답이다.
%     Python 포팅도 같은 정의를 쓰므로, 셋이 맞으면 세 구현이 일치하는 것이고
%     갈리면 그 자리가 발견이다.
%
% 사용법
%   addpath('dd_shims')          % ← 반드시 명시적으로. 조용히 켜지면 안 된다
%   dd_eval()                    % 기본: pristine · GITT · Si=Li · w_dqdv=0
%   dd_eval('State','300_0009','SiSource','Kunz')
%
% 옵션
%   'HalfCellDir'  기본 'data/half_cell/GITT/'
%   'SiSource'     기본 'Li'
%   'State'        기본 'pristine'
%   'WDqdv'        기본 0        (1 이면 findpeaks 대체품이 더 필요하다)
%   'P'            평가할 파라미터 행렬 (n x 5). 비우면 아래 기본 격자
%   'Out'          CSV 경로

    p = inputParser;
    p.addParameter('HalfCellDir', 'data/half_cell/GITT/');
    p.addParameter('SiSource', 'Li');
    p.addParameter('State', 'pristine');
    p.addParameter('WDqdv', 0);
    p.addParameter('P', []);
    p.addParameter('Out', '');
    p.parse(varargin{:});
    o = p.Results;

    if isempty(which('sgolayfilt'))
        error('dd_eval: sgolayfilt 가 없다 — `addpath(''dd_shims'')` 를 먼저 하라');
    end
    if o.WDqdv ~= 0 && isempty(which('findpeaks'))
        error(['dd_eval: WDqdv~=0 은 findpeaks 가 필요하다. 지금은 대체품이 ' ...
               '없으므로 WDqdv=0 으로 대조하라 (그것이 그들 기본 설정이다).']);
    end

    diff_params = struct('window', 11, 'poly_order', 3);

    % ── 그들 코드로 곡선을 만든다 ──
    hc = local_halfcell_name(o.HalfCellDir, o.State);
    ro = electrode_ocv(o.HalfCellDir, hc, diff_params);
    lit = local_load_lit(o.SiSource);
    [E_NE, dv_NE] = build_blend_functions(lit.Si_capacity, lit.Si_voltage, ...
                                          lit.Gr_capacity, lit.Gr_voltage, diff_params);

    % ── 풀셀 (electrode_balancing_blend.m 과 같은 전처리) ──
    [cap, vol] = local_fullcell(o.State);
    [cap, vol] = averageDuplicates(cap, vol);
    c_cell = cap(end);
    if vol(1) < vol(end)
        cap = cap / c_cell;
    else
        cap = 1 - cap / c_cell;
    end

    d = differential(cap, vol, diff_params.window, diff_params.poly_order);
    lo = quantile(d.capacity_uniform2, 0.15);
    hi = quantile(d.capacity_uniform2, 0.85);
    idx = (d.capacity_uniform2 >= lo) & (d.capacity_uniform2 <= hi);
    cap_dv = d.capacity_uniform2(idx);
    dv_dat = d.dvdq(idx);

    fprintf('\n=== dd_eval ===\n');
    fprintf('state=%s  halfcell=%s  Si=%s  w_dqdv=%g\n', o.State, o.HalfCellDir, o.SiSource, o.WDqdv);
    fprintf('c_cell            = %.6f\n', c_cell);
    fprintf('dv 창 (15%%,85%%)   = [%.10f, %.10f]  (n=%d)\n', lo, hi, sum(idx));
    vlo = quantile(d.voltage_uniform, 0.05);
    vhi = quantile(d.voltage_uniform, 0.95);
    fprintf('dq 창 (5%%,95%%)    = [%.10f, %.10f]\n', vlo, vhi);
    fprintf('E_PE(0.5)         = %.10f\n', ro.E_PE(0.5));
    fprintf('E_NE(0.5, 0.25)   = %.10f\n', E_NE(0.5, 0.25));
    fprintf('dv_PE(0.5)        = %.10f\n', ro.dv_PE(0.5));
    fprintf('dv_NE(0.5, 0.25)  = %.10f\n\n', dv_NE(0.5, 0.25));

    % ── 평가할 파라미터 ──
    P = o.P;
    if isempty(P)
        % 그들이 보고한 값(pristine·GITT·Li)과 그 주변, 그리고 γ 격자
        P = [1.077218 -0.022949 1.001342 0.000309 0.295099;
             1.076074 -0.022129 1.001279 0.000299 0.295298;
             1.181472 -0.141171 1.080759 -0.000775 0.239466;
             1.080000 -0.040000 1.050000 -0.030000 0.250000;
             1.100000 -0.050000 1.100000 -0.010000 0.100000;
             1.100000 -0.050000 1.100000 -0.010000 0.200000;
             1.100000 -0.050000 1.100000 -0.010000 0.300000;
             1.100000 -0.050000 1.100000 -0.010000 0.400000];
    end

    rows = {};
    fprintf('a_PE,b_PE,a_NE,b_NE,gamma_Si,rmse_pocv,rmse_dvdq\n');
    for k = 1:size(P, 1)
        q = P(k, :);
        e_model  = ro.E_PE((cap - q(2)) / q(1)) - E_NE((cap - q(4)) / q(3), q(5));
        r_pocv   = sqrt(mean((vol - e_model) .^ 2));
        dv_model = ro.dv_PE((cap_dv - q(2)) / q(1)) - dv_NE((cap_dv - q(4)) / q(3), q(5));
        r_dvdq   = sqrt(mean((dv_dat - dv_model) .^ 2));
        rows{end+1} = sprintf('%.6f,%.6f,%.6f,%.6f,%.6f,%.10f,%.10f', ...
            q(1), q(2), q(3), q(4), q(5), r_pocv, r_dvdq); %#ok<AGROW>
        fprintf('%s\n', rows{end});
    end

    if ~isempty(o.Out)
        fid = fopen(o.Out, 'w');
        fprintf(fid, 'a_PE,b_PE,a_NE,b_NE,gamma_Si,rmse_pocv,rmse_dvdq\n');
        for k = 1:numel(rows), fprintf(fid, '%s\n', rows{k}); end
        fclose(fid);
        fprintf('\nwrote %s\n', o.Out);
    end
end

% ══════════════════════════════════════════════════════════════════════
function name = local_halfcell_name(dirpath, state)
    if contains(dirpath, '005C')
        name = sprintf('%s_005C.xlsx', state);
    else
        name = sprintf('%s.xlsx', state);
    end
end

function [c, v] = local_fullcell(state)
    d = dir(fullfile('data','full_cell','large_cell_033C','*.xlsx'));
    f = '';
    for k = 1:numel(d)
        if ~contains(d(k).name, 'pristine') && ~contains(d(k).name, '300cycle')
            f = fullfile(d(k).folder, d(k).name); break
        end
    end
    if isempty(f), error('dd_eval: 풀셀 워크북을 못 찾았다'); end
    order = {'pristine','100','200','300_0009','300_0147'};
    col = find(strcmp(order, state), 1);
    if isempty(col), error('dd_eval: 모르는 state "%s"', state); end
    M = readmatrix(f, 'Range', 'A3');
    c = M(:, 2*col-1); v = M(:, 2*col);
    ok = ~isnan(c) & ~isnan(v);
    c = c(ok); v = v(ok);
end

function lit = local_load_lit(si_source)
    lit_dir = fullfile('data','literature');
    g = readtable(fullfile(lit_dir, 'Si_Gr_literature_OCP.xlsx'));
    s = readtable(fullfile(lit_dir, 'Si_OCP_sources', [si_source '.csv']));
    lit = struct('Si_capacity', s.normalizedCapacity, 'Si_voltage', s.voltage, ...
                 'Gr_capacity', g.Gr_capacity(~isnan(g.Gr_capacity)), ...
                 'Gr_voltage',  g.Gr_voltage(~isnan(g.Gr_voltage)));
end
