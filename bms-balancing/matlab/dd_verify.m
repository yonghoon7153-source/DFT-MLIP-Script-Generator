function dd_verify(mode, varargin)
%DD_VERIFY  α·β 검증 드라이버 — 규진팀 코드를 **고치지 않고** 그대로 호출한다.
%
%   이 파일은 `electrode_balancing_blend.m` 와 같은 폴더(프로젝트 루트)에 둔다.
%   기존 함수(electrode_ocv · electrode_balancing_blend · build_blend_functions ·
%   extractMyData · averageDuplicates)를 그대로 부르므로, 여기서 나오는 값은
%   **그들 파이프라인의 값**이다.
%
%   왜 필요한가: Python 포팅(`bms-balancing/`)이 재는 축퇴가 진짜 그들 모델의
%   성질인지 확인하려면, **같은 것을 MATLAB 에서도 찍어 봐야** 한다. 포팅이
%   틀렸으면 그 위의 모든 숫자가 틀린다.
%
% 사용법
%   dd_verify('dump')                 % 여러 설정에서 적합 결과를 한 줄씩 출력
%   dd_verify('profile')              % γ_Si 를 고정하고 나머지 넷 재적합
%   dd_verify('scalenoise')           % 같은 설정을 5번 — 목적함수 scale 의 난수 영향
%
% 옵션 (이름-값)
%   'HalfCellDir'  기본 'data/half_cell/GITT/'
%   'FullCellFile' 기본 자동 탐색 (data/full_cell/large_cell_033C/*.xlsx 중 2행 헤더)
%   'SiSource'     기본 'Li'      ('Baggetto','Friedrich','Jiang','Kunz','Li','Lu','Sethuraman','Wetjen')
%   'State'        기본 '300_0009'
%   'RefState'     기본 'pristine'
%   'WDqdv'        기본 0          (1 이면 dQ/dV 항 포함)
%   'Gammas'       기본 0:0.025:0.5 (profile 모드)
%   'Out'          기본 ''         (비우면 화면만, 주면 그 CSV 로 저장)
%
% 출력은 **CSV 한 줄씩**이라 그대로 Python 쪽 표와 대조할 수 있다.

    if nargin < 1, mode = 'dump'; end

    p = inputParser;
    p.addParameter('HalfCellDir', 'data/half_cell/GITT/');
    p.addParameter('FullCellFile', '');
    p.addParameter('SiSource', 'Li');
    p.addParameter('State', '300_0009');
    p.addParameter('RefState', 'pristine');
    p.addParameter('WDqdv', 0);
    p.addParameter('Gammas', 0:0.025:0.5);
    p.addParameter('Out', '');
    p.parse(varargin{:});
    o = p.Results;

    if isempty(o.FullCellFile)
        o.FullCellFile = local_find_fullcell();
    end

    % ── 공통 설정 — main_blend_final.m 과 **같은 값**을 쓴다 ──
    diff_params = struct('window', 11, 'poly_order', 3);
    fit_params  = struct('peak_weight', 7, 'sigma_ratio', 0.03, ...
                         'use_peak_weight', true, 'weight_pe_peaks', false, ...
                         'w_pocv', 1.0, 'w_dvdq', 1.0, 'w_dqdv', o.WDqdv);
    initial5 = [1.08, -0.04, 1.05, -0.03, 0.25];
    lb5      = [1.0,  -0.5,  1.0,  -0.5,  0.00];
    ub5      = [1.4,   0,    1.4,   0.1,  0.50];

    lit = local_load_lit(o.SiSource);

    switch lower(mode)
    case 'dump'
        rows = {};
        for w = unique([o.WDqdv, o.WDqdv])
            fp = fit_params; fp.w_dqdv = w;
            for si = {'Baggetto','Friedrich','Jiang','Kunz','Li','Lu','Sethuraman','Wetjen'}
                L = local_load_lit(si{1});
                rng(0, 'twister');    % ★ 발견 4 — 원본은 seed 가 없다. 비교하려면 고정해야 한다
                r0 = local_fit(o.RefState, o, L, initial5, lb5, ub5, diff_params, fp);
                rng(0, 'twister');
                r1 = local_fit(o.State,    o, L, initial5, lb5, ub5, diff_params, fp);
                m  = local_modes(r0, r1);
                rows{end+1} = local_row(si{1}, w, r1, m, lb5, ub5); %#ok<AGROW>
                fprintf('%s\n', rows{end});
            end
        end
        local_save(o.Out, {'si_source,w_dqdv,a_PE,b_PE,a_NE,b_NE,gamma_Si,rmse_pocv,rmse_dvdq,LAM_PE_pct,LAM_NE_pct,LLI_pct,bounds'}, rows);

    case 'profile'
        rng(0, 'twister');
        r0 = local_fit(o.RefState, o, lit, initial5, lb5, ub5, diff_params, fit_params);
        rows = {};
        fprintf('gamma_Si,a_PE,b_PE,a_NE,b_NE,rmse_pocv_mV,LAM_PE_pct,LAM_NE_pct,LLI_pct,bounds\n');
        for g = o.Gammas
            lbg = lb5; ubg = ub5; ini = initial5;
            lbg(5) = g; ubg(5) = g; ini(5) = g;      % γ 를 못 움직이게 묶는다
            rng(0, 'twister');
            r = local_fit(o.State, o, lit, ini, lbg, ubg, diff_params, fit_params);
            m = local_modes(r0, r);
            rows{end+1} = sprintf('%.4f,%.6f,%.6f,%.6f,%.6f,%.3f,%.4f,%.4f,%.4f,%s', ...
                g, r.a_PE, r.b_PE, r.a_NE, r.b_NE, 1000*r.rmse_pocv, ...
                m.LAM_PE*100, m.LAM_NE*100, m.LLI*100, ...
                local_bounds([r.a_PE r.b_PE r.a_NE r.b_NE], lb5(1:4), ub5(1:4))); %#ok<AGROW>
            fprintf('%s\n', rows{end});
        end
        local_save(o.Out, {'gamma_Si,a_PE,b_PE,a_NE,b_NE,rmse_pocv_mV,LAM_PE_pct,LAM_NE_pct,LLI_pct,bounds'}, rows);

    case 'scalenoise'
        % ★ 발견 4 를 눈으로 본다 — seed 만 바꿔 같은 적합을 5번
        rows = {};
        fprintf('seed,a_PE,b_PE,a_NE,b_NE,gamma_Si,rmse_pocv_mV\n');
        for s = 0:4
            rng(s, 'twister');
            r = local_fit(o.State, o, lit, initial5, lb5, ub5, diff_params, fit_params);
            rows{end+1} = sprintf('%d,%.6f,%.6f,%.6f,%.6f,%.6f,%.3f', ...
                s, r.a_PE, r.b_PE, r.a_NE, r.b_NE, r.gamma_Si, 1000*r.rmse_pocv); %#ok<AGROW>
            fprintf('%s\n', rows{end});
        end
        local_save(o.Out, {'seed,a_PE,b_PE,a_NE,b_NE,gamma_Si,rmse_pocv_mV'}, rows);

    otherwise
        error('dd_verify: 모르는 mode "%s" (dump|profile|scalenoise)', mode);
    end
end

% ══════════════════════════════════════════════════════════════════════
function r = local_fit(state, o, lit, initial5, lb5, ub5, diff_params, fit_params)
    hc = local_halfcell_name(o.HalfCellDir, state);
    result_ocv = electrode_ocv(o.HalfCellDir, hc, diff_params);

    [c_full, v_full] = local_fullcell(o.FullCellFile, state);
    T = table(c_full, v_full, 'VariableNames', {'0_capacity','0_voltage'});
    tmp = sprintf('dd_verify_%s.xlsx', matlab.lang.makeValidName(state));
    writetable(T, fullfile(tempdir, tmp));

    r = electrode_balancing_blend(result_ocv, lit, tempdir, tmp, 0, ...
        initial5, lb5, ub5, "combined", "none", diff_params, fit_params);
end

function m = local_modes(r0, r)
    % main_blend_final.m 의 식 그대로
    m.LAM_PE = (r0.a_PE*r0.c_cell - r.a_PE*r.c_cell) / (r0.a_PE*r0.c_cell);
    m.LAM_NE = (r0.a_NE*r0.c_cell - r.a_NE*r.c_cell) / (r0.a_NE*r0.c_cell);
    c_lit_i  = (r0.a_PE + r0.b_PE - r0.b_NE) * r0.c_cell;
    c_lit    = (r.a_PE  + r.b_PE  - r.b_NE ) * r.c_cell;
    m.LLI    = (c_lit_i - c_lit) / c_lit_i;
end

function s = local_row(si, w, r, m, lb5, ub5)
    s = sprintf('%s,%g,%.6f,%.6f,%.6f,%.6f,%.6f,%.6g,%.6g,%.4f,%.4f,%.4f,%s', ...
        si, w, r.a_PE, r.b_PE, r.a_NE, r.b_NE, r.gamma_Si, ...
        r.rmse_pocv, r.rmse_dvdq, m.LAM_PE*100, m.LAM_NE*100, m.LLI*100, ...
        local_bounds([r.a_PE r.b_PE r.a_NE r.b_NE r.gamma_Si], lb5, ub5));
end

function s = local_bounds(p, lb, ub)
    names = {'a_PE','b_PE','a_NE','b_NE','gamma_Si'};
    hit = {};
    for i = 1:numel(p)
        if abs(p(i) - lb(i)) < 1e-6, hit{end+1} = [names{i} '=lb']; end %#ok<AGROW>
        if abs(p(i) - ub(i)) < 1e-6, hit{end+1} = [names{i} '=ub']; end %#ok<AGROW>
    end
    if isempty(hit), s = '-'; else, s = strjoin(hit, '|'); end
end

function name = local_halfcell_name(dirpath, state)
    if contains(dirpath, '005C')
        name = sprintf('%s_005C.xlsx', state);
    else
        name = sprintf('%s.xlsx', state);
    end
end

function f = local_find_fullcell()
    d = dir(fullfile('data','full_cell','large_cell_033C','*.xlsx'));
    keep = {};
    for k = 1:numel(d)
        if ~contains(d(k).name, 'pristine') && ~contains(d(k).name, '300cycle')
            keep{end+1} = fullfile(d(k).folder, d(k).name); %#ok<AGROW>
        end
    end
    if isempty(keep)
        error('dd_verify: data/full_cell/large_cell_033C 에서 상태별 워크북을 못 찾았다');
    end
    f = keep{1};
end

function [c, v] = local_fullcell(file, state)
    % 2행 헤더(1행=상태명, 2행=단위)에서 그 상태의 컬럼쌍
    order = {'pristine','100','200','300_0009','300_0147'};
    col = find(strcmp(order, state), 1);
    if isempty(col)
        error('dd_verify: 모르는 state "%s"', state);
    end
    M = readmatrix(file, 'Range', 'A3');
    c = M(:, 2*col-1);
    v = M(:, 2*col);
    ok = ~isnan(c) & ~isnan(v);
    c = c(ok); v = v(ok);
end

function lit = local_load_lit(si_source)
    lit_dir = fullfile('data','literature');
    g = readtable(fullfile(lit_dir, 'Si_Gr_literature_OCP.xlsx'));
    Gr_c = g.Gr_capacity(~isnan(g.Gr_capacity));
    Gr_v = g.Gr_voltage(~isnan(g.Gr_voltage));
    s = readtable(fullfile(lit_dir, 'Si_OCP_sources', [si_source '.csv']));
    lit = struct('Si_capacity', s.normalizedCapacity, 'Si_voltage', s.voltage, ...
                 'Gr_capacity', Gr_c, 'Gr_voltage', Gr_v);
end

function local_save(out, header, rows)
    if isempty(out), return; end
    fid = fopen(out, 'w');
    fprintf(fid, '%s\n', header{1});
    for k = 1:numel(rows)
        fprintf(fid, '%s\n', rows{k});
    end
    fclose(fid);
    fprintf('\nwrote %s\n', out);
end
