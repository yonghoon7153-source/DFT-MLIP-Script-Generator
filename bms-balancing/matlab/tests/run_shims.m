function run_shims(mode, outfile)
%RUN_SHIMS  dd_shims 의 수치를 CSV 로 떨군다 — 세 구현 대조용.
%   mode='native' : Octave 내장 quantile (method 5 = MATLAB 정의) — 기준값
%   mode='shim'   : dd_shims/ 를 경로에 올린 우리 대체 구현
  % mode: 'shim' (dd_shims 를 경로에) 또는 'native' (옥타브 내장)
  if strcmp(mode,'shim'), addpath('dd_shims'); end
  P = dlmread('cases/pvals.csv');
  names = {'n1','n2','n4_int','n5_unsort','n7_dup','n50_rand','n101_ramp','n500_ocv'};
  fid = fopen(outfile,'w');
  fprintf(fid,'kind,vec,arg1,arg2,idx,value\n');
  for i=1:numel(names)
    x = dlmread(['cases/vec_' names{i} '.csv']);
    for j=1:numel(P)
      q = quantile(x, P(j));
      fprintf(fid,'quantile,%s,%.17g,,1,%.17g\n', names{i}, P(j), q);
    end
  end
  % sgolayfilt 는 shim 모드에서만 (옥타브 core 에 없다)
  if strcmp(mode,'shim')
    T = fopen('cases/sgcases.csv'); fgetl(T);
    while true
      L = fgetl(T); if ~ischar(L), break; end
      parts = strsplit(L, ',');
      vn = parts{1}; od = str2double(parts{2}); fl = str2double(parts{3});
      x = dlmread(['cases/vec_' vn '.csv']);
      y = sgolayfilt(x, od, fl);
      for k=1:numel(y)
        fprintf(fid,'sgolay,%s,%d,%d,%d,%.17g\n', vn, od, fl, k, y(k));
      end
    end
    fclose(T);
  end
  fclose(fid);
  printf('wrote %s\n', outfile);
end
