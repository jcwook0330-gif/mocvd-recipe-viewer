import streamlit as st
import re
import matplotlib.pyplot as plt

# --------------------------
# 함수 정의
# --------------------------

def parse_recipe(file):
    data = []
    current_time = 0

    for line in file:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # 시간 정보 파싱
        time_match = re.match(r"^(\d+:\d+:\d+|\d+)", line)
        if time_match:
            time_str = time_match.group(1)
            if ':' in time_str:
                h, m, s = map(int, time_str.split(":"))
                current_time = h * 3600 + m * 60 + s
            else:
                current_time += int(time_str)

        # 변수와 값 추출
        for match in re.finditer(r"([\w\.]+)\s*=\s*([\w\d\.]+)", line):
            var, val = match.groups()
            try:
                val = float(val)
            except:
                continue
            data.append((current_time, var, val))

    return data

def get_variable_list(parsed_data):
    return sorted(list(set(var for _, var, _ in parsed_data)))

def extract_variable_series(parsed_data, var_name):
    times = []
    values = []
    for t, v, val in parsed_data:
        if v == var_name:
            times.append(t)
            values.append(val)
    return times, values

# --------------------------
# Streamlit 인터페이스
# --------------------------

st.title("📈 MOCVD 레시피 시각화 앱")
st.markdown("업로드한 레시피 파일에서 시간에 따른 파라미터 변화를 그래프로 시각화합니다.")

uploaded_file = st.file_uploader("📤 레시피 파일을 업로드하세요 (.txt)", type=["txt"])

if uploaded_file is not None:
    lines = uploaded_file.read().decode("utf-8").splitlines()
    parsed = parse_recipe(lines)

    if parsed:
        var_list = get_variable_list(parsed)
        var_select = st.multiselect("📌 시각화할 변수 선택", var_list, default=["ReactorTemp", "ReactorPress"])

        # 그래프 출력
        fig, ax = plt.subplots()
        for var in var_select:
            t, v = extract_variable_series(parsed, var)
            ax.plot(t, v, label=var)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Value")
        ax.set_title("MOCVD Recipe Parameter Plot")
        ax.legend()
        st.pyplot(fig)

    else:
        st.warning("파싱 가능한 데이터가 없습니다.")
