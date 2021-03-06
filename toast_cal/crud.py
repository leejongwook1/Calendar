from django.http import HttpResponse
from django.core import serializers
from .models import *
from django.db.models.aggregates import Count
from json import dumps
import datetime


# 서버에서 ajax로 일정 보내주는 함수
def ourstores(request):
    stores_list = Calendar.objects.filter(userID=request.session["userID"])

    return HttpResponse(
        serializers.serialize("json", stores_list), content_type="application/json"
    )


# calendar 초기세팅 데이터 보내주는 함수
def calSetData(request):
    calData = CalID.objects.all()

    return HttpResponse(
        serializers.serialize("json", calData), content_type="application/json"
    )


# ajax로 들어온 데이터를 db에 ORM사용 저장
def createData(request):
    if request.method == "POST":
        new_instance = Calendar.objects.create(
            userID=request.session["userID"],
            calendarId=request.POST["calendarId"],
            title=request.POST["title"],
            category=request.POST["category"],
            location=request.POST["location"],
            start=request.POST["start"],
            end=request.POST["end"],
            isAllDay=request.POST["isAllDay"],
            state=request.POST["state"],
            calendarClass=request.POST["class"],
        )
        new_instance.save()

        return HttpResponse(new_instance.id)


# ajax로 들어온 데이터를 db에 ORM사용 수정
def updateData(request):
    if request.method == "POST":
        update = Calendar.objects.filter(pk=request.POST["id"]).update(
            calendarId=request.POST["calendarId"],
            title=request.POST["title"],
            category=request.POST["category"],
            location=request.POST["location"],
            start=request.POST["start"],
            end=request.POST["end"],
            isAllDay=request.POST["isAllDay"],
            state=request.POST["state"],
            calendarClass=request.POST["class"],
        )
        # 더미데이터로 응답
        return HttpResponse(1)


# ajax로 들어온 pk값으로 데이터 삭제
def deleteData(request):
    if request.method == "POST":
        query = Calendar.objects.get(pk=request.POST["id"])
        query.delete()
        # 더미데이터로 응답
        return HttpResponse(1)


# 학생 기능
# 왼쪽 사이드바 체크시 데이터를 보내줌
def checked(request):
    if request.method == "POST":
        checked_list = Calendar.objects.filter(
            userID=request.session["userID"], calendarId=request.POST["checked"]
        )

    return HttpResponse(
        serializers.serialize("json", checked_list), content_type="application/json"
    )


# 메뉴
# 학과 데이터 반환
def department(request):
    if request.session["userType"] == "student":
        department_list = Department.objects.all().order_by("name")
    elif request.session["userType"] == "professor":
        pro_department = Professor.objects.get(
            userID=request.session["userID"]
        ).department
        # print(pro_department)
        department_list = Department.objects.filter(name=pro_department).order_by(
            "name"
        )

    return HttpResponse(
        serializers.serialize("json", department_list), content_type="application/json"
    )


# 학과 선택시 해당 과목반환
def subject(request):
    subject_list = Subject.objects.filter(
        department=request.POST.get("name", None)
    ).order_by("name")

    return HttpResponse(
        serializers.serialize("json", subject_list), content_type="application/json"
    )


# 과목 선택시 해당 이수구분 반환
def chanege_type(request):
    lecture_type = Subject.objects.filter(name=request.POST.get("name", None))

    return HttpResponse(
        serializers.serialize("json", lecture_type), content_type="application/json"
    )


# 조회 버튼
def lecture_lookup(request):
    if request.method == "POST":
        department = request.POST.get("department")
        subject = request.POST.get("subject")
        lecture_type = request.POST.get("lecture_type")
        if subject == "전체":
            if lecture_type == "일반교양" or lecture_type == "전체":
                subject = Subject.objects.filter(department=department)

                return HttpResponse(
                    serializers.serialize("json", subject),
                    content_type="application/json",
                )
            else:
                subject = Subject.objects.filter(
                    department=department, lecture_type=lecture_type
                )

                return HttpResponse(
                    serializers.serialize("json", subject),
                    content_type="application/json",
                )
        else:
            if lecture_type == "일반교양" or lecture_type == "전체":
                subject = Subject.objects.filter(department=department, name=subject)

                return HttpResponse(
                    serializers.serialize("json", subject),
                    content_type="application/json",
                )
            else:
                subject = Subject.objects.filter(
                    department=department, name=subject, lecture_type=lecture_type
                )

                return HttpResponse(
                    serializers.serialize("json", subject),
                    content_type="application/json",
                )


# 과목 저장
def lecture_save(request):
    if request.method == "POST":
        boolean_name = Student_lecture.objects.filter(
            student_id=request.session["userID"], name=request.POST["name"],
        ).exists()

        request_period = request.POST["period"].split()
        first_period = Student_lecture.objects.filter(
            student_id=request.session["userID"], period__icontains=request_period[0]
        ).exists()
        second_period = Student_lecture.objects.filter(
            student_id=request.session["userID"], period__icontains=request_period[1]
        ).exists()
        Count = Subject.objects.get(
            code=request.POST["code"], codeClass=request.POST["codeClass"]
        )

        if Count.stdCount < Count.total_stdCount:
            if boolean_name or first_period or second_period:
                return HttpResponse("중복된 데이터입니다. 수강 강의를 확인하세요.")
            else:
                new_instance = Student_lecture.objects.create(
                    student_id=request.session["userID"],
                    code=request.POST["code"],
                    department=request.POST["department"],
                    lecture_type=request.POST["lecture_type"],
                    codeClass=request.POST["codeClass"],
                    name=request.POST["name"],
                    professor=request.POST["professor"],
                    period=request.POST["period"],
                )
                obj = Subject.objects.get(code=new_instance.code)
                obj.stdCount += 1
                obj.save()
                return HttpResponse("저장 성공")
        else:
            return HttpResponse("수강 인원이 초과된 과목입니다.")


# 학생 강의 불러오기
def student_lecture_load(request):
    if request.method == "POST":
        date_list = Student_lecture.objects.filter(
            student_id=request.session["userID"]
        ).order_by("code")
        return HttpResponse(
            serializers.serialize("json", date_list), content_type="application/json"
        )


# 학생 강의 삭제
def student_lecture_delete(request):
    if request.method == "POST":
        for data in range(int(len(request.POST) / 7)):
            query = Student_lecture.objects.get(
                student_id=request.session["userID"],
                code=request.POST["array[" + str(data) + "][code]"],
                codeClass=request.POST["array[" + str(data) + "][codeClass]"],
            )
            query.delete()
            obj = Subject.objects.get(code=query.code)
            obj.stdCount -= 1
            obj.save()
        date_list = Student_lecture.objects.filter(student_id=request.session["userID"])
        return HttpResponse(
            serializers.serialize("json", date_list), content_type="application/json"
        )


# 학생 강의 투표 테이블 데이터 불러오기
def stdVoteJoinTable(request):

    finalData = Vote.objects.filter(classCode="NULL")  # 초기화

    if request.POST["lecture_type"] == "전체":
        lec_list = Student_lecture.objects.filter(student_id=request.session["userID"],)
        for data in lec_list:
            finalData = finalData | Vote.objects.filter(
                classCode=data.code, voteStatus="투표 중"
            )
    else:
        lec_list = Student_lecture.objects.filter(
            student_id=request.session["userID"],
            lecture_type=request.POST["lecture_type"],
        )
        for data in lec_list:
            finalData = finalData | Vote.objects.filter(
                classCode=data.code, voteStatus="투표 중"
            )

    return HttpResponse(
        serializers.serialize("json", finalData), content_type="application/json"
    )


def joinCheck(request):
    if request.method == "POST":
        checkVote = Vote.objects.filter(classCode="Null")
        stdJoin = VoteInfo.objects.filter(voteId="0")

        for i in range(int(len(request.POST) / 4)):
            classCode = request.POST["array[" + str(i) + "][classCode]"]
            checkVote = checkVote | Vote.objects.filter(classCode=classCode)

        for i in range(checkVote.count()):
            stdJoin = stdJoin | VoteInfo.objects.filter(
                voteId=checkVote[i].id, studentID=request.session["userID"]
            )

    return HttpResponse(
        serializers.serialize("json", stdJoin), content_type="application/json"
    )


# 투표 하위 테이블에 투표정보 저장 (+ 투표 테이블 업데이트)
def takeVoteSave(request):
    # request.POST
    voteData = Vote.objects.filter(id=request.POST["array[0][id]"])
    # print(checkData)

    checkData = VoteInfo.objects.filter(
        voteId=request.POST["array[0][id]"], studentID=request.session["userID"]
    )

    if checkData:
        if checkData[0].studentID == request.session["userID"]:
            return HttpResponse("이미 투표하셨습니다!")

    if request.POST["array[0][time]"] != "False":
        voteData.update(choice1=voteData[0].choice1 + 1)
    if request.POST["array[1][time]"] != "False":
        voteData.update(choice2=voteData[0].choice2 + 1)
    if request.POST["array[2][time]"] != "False":
        voteData.update(choice3=voteData[0].choice3 + 1)
    if request.POST["array[3][time]"] != "False":
        voteData.update(choice4=voteData[0].choice4 + 1)

    voteInfoData = VoteInfo.objects.create(
        voteId=request.POST["array[0][id]"],
        studentID=request.session["userID"],
        comment=request.POST["array[4][comment]"],
    )

    voteStatusData = Vote.objects.filter(id=request.POST["array[0][id]"])

    checkEnd = (
        voteStatusData[0].choice1
        + voteStatusData[0].choice2
        + voteStatusData[0].choice3
        + voteStatusData[0].choice4
    )
    if checkEnd == voteStatusData[0].totalCount:
        voteStatusData.update(voteStatus="투표 마감")

    return HttpResponse("투표 완료!")


# 학생 강의 투표 테이블에서 투표하기 선택시 아래에 보여지는 데이터 불러오기
def stdVoteSelectData(request):
    # print(request.POST)
    voteSelectData = Vote.objects.filter(classCode=request.POST["code"])

    return HttpResponse(
        serializers.serialize("json", voteSelectData), content_type="application/json"
    )


# vote 테이블의 아무값이나 받은 테스트 데이터
def voteSelectTest(request):
    stores_list = Vote.objects.filter(reject_votes=request.POST["reject_votes"],)

    return HttpResponse(
        serializers.serialize("json", stores_list), content_type="application/json"
    )


# 학생투표페이지의 강의정보
# 로직상 맞는 구조지만,과목테이블에서 투표테이블로 맞춰서 출력할것임.
def getLectureInfo(request):
    lecCode = request.POST["code"]
    # print(request.POST["code"])

    subject_data = Subject.objects.filter(code=lecCode)
    # print(subject_data)

    return HttpResponse(
        serializers.serialize("json", subject_data), content_type="application/json"
    )


# 교수 기능
# ajax로 필터링하여 table 생성할 값 반환
def voteTable(request):
    if request.POST["lecture_type"] == "전체" and request.POST["vote_status"] != "전체":
        stores_list = Vote.objects.filter(
            proName=request.session["userName"], voteStatus=request.POST["vote_status"],
        )
    elif request.POST["lecture_type"] != "전체" and request.POST["vote_status"] == "전체":
        stores_list = Vote.objects.filter(
            proName=request.session["userName"], lecType=request.POST["lecture_type"],
        )
    elif request.POST["lecture_type"] == "전체" and request.POST["vote_status"] == "전체":
        stores_list = Vote.objects.filter(proName=request.session["userName"],)
    else:
        stores_list = Vote.objects.filter(
            proName=request.session["userName"],
            lecType=request.POST["lecture_type"],
            voteStatus=request.POST["vote_status"],
        )
    return HttpResponse(
        serializers.serialize("json", stores_list), content_type="application/json"
    )


# ajax로 필터링하여 chart를 만들기 위한 값 반환
def voteChart(request):
    stores_list = Vote.objects.filter(classCode=request.POST["code"])

    return HttpResponse(
        serializers.serialize("json", stores_list), content_type="application/json"
    )


# 투표 확정1 (투표를 확정할 데이터를 보내주는 부분)
def voteConfirm(request):

    voteData = Vote.objects.get(classCode=request.POST["code"])

    voteTimeData = ""
    finalData = ""

    finalData += voteData.classCode + ","
    finalData += voteData.className + ","

    # list는 투표수가 가장 많은 선택지의 값을 뽑기 위해 만듬
    # dict는 투표수가 가장 많은 시간 데이터를 뽑기 위해 만듬
    voteList = [voteData.choice1, voteData.choice2, voteData.choice3, voteData.choice4]
    voteDict = {
        "choice1": voteData.choice1_Title,
        "choice2": voteData.choice2_Title,
        "choice3": voteData.choice3_Title,
        "choice4": voteData.choice4_Title,
    }

    maxValue = max(voteList)  # 투표를 가장 많이 한 선택지

    for i, vdata in zip(range(0, 4), voteList):
        if vdata == maxValue:
            voteTimeData = voteDict["choice" + str(i + 1)]
            break

    finalData += voteTimeData

    return HttpResponse(finalData)


# ajax로 들어온 데이터로 강의 개설
def makeSubject(request):
    if request.method == "POST":
        if Subject.objects.filter(
            code=request.POST["code"], codeClass=request.POST["codeClass"]
        ).exists():
            return HttpResponse("강의 코드가 겹치는 강의가 있습니다.")

        splitdata1, splitdata2 = request.POST["period"].split(" ")

        if splitdata1 == splitdata2:
            return HttpResponse("강의 시간이 겹치지 않게 설정해주세요")

        makedData = Subject.objects.create(
            name=request.POST["name"],
            code=request.POST["code"],
            codeClass=request.POST["codeClass"],
            professor=request.session["userName"],
            period=request.POST["period"],
            lecture_type=request.POST["lecture_type"],
            department=request.POST["department"],
            stdCount=0,
            total_stdCount=request.POST["total_count"],
        )
        makedData.save()

        createdData = Subject.objects.filter(id=makedData.id)
        return HttpResponse(
            serializers.serialize("json", createdData), content_type="application/json"
        )


# 교수 강의 테이블 출력
def pro_lecture_table(request):
    if request.method == "POST":
        userID = request.session["userID"]
        professor = Professor.objects.get(userID=userID)
        pro_subject = Subject.objects.filter(
            professor=professor.username, department=professor.department
        )

        return HttpResponse(
            serializers.serialize("json", pro_subject), content_type="application/json"
        )


# 교수 강의 삭제
def professor_lecture_delete(request):
    if request.method == "POST":
        code = request.POST["code"]

        lec_del = Student_lecture.objects.filter(code=request.POST["code"])
        if lec_del:
            lec_del.delete()

        vote_del = Vote.objects.filter(classCode=code)
        ava_del = Ava_Time.objects.filter(classCode=code)
        pubcal_del = PubCalendar.objects.filter(code=code)

        if vote_del:
            info_del = VoteInfo.objects.filter(voteId=vote_del[0].id)

            vote_del.delete()
            ava_del.delete()
            info_del.delete()
            pubcal_del.delete()

        sub_del = Subject.objects.get(
            code=request.POST["code"], codeClass=request.POST["codeClass"]
        )
        sub_del.delete()

        date_list = Subject.objects.filter(professor=request.session["userName"])

        return HttpResponse(
            serializers.serialize("json", date_list), content_type="application/json"
        )


def subject_info(request):
    if request.method == "POST":
        stores_list = Subject.objects.filter(code=request.POST["classCode"])

        return HttpResponse(
            serializers.serialize("json", stores_list), content_type="application/json"
        )


# 공통 기능
# right nav 부분 ajax 통신
def dateList(request):
    if request.method == "POST":

        date_list = Calendar.objects.filter(
            userID=request.session["userID"],
            start__startswith=request.POST["todayData"],
            end__startswith=request.POST["todayData"],
        )
    return HttpResponse(
        serializers.serialize("json", date_list), content_type="application/json"
    )


def getWeekSchedule(request):
    if request.method == "POST":
        date_list = Calendar.objects.filter(
            userID=request.session["userID"],
            start__range=[request.POST["StartDate"], request.POST["EndDate"]],
        ).order_by("start")

    return HttpResponse(
        serializers.serialize("json", date_list), content_type="application/json"
    )


# ajax로 들어온 데이터들로 calendar DB에 저장
def makeCalendars(request):
    for i in range(int(len(request.POST) / 10)):
        new_instance = Calendar.objects.create(
            userID=request.session["userID"],
            calendarId=request.POST["scheduleData[" + str(i) + "][calendarId]"],
            title=request.POST["scheduleData[" + str(i) + "][title]"],
            category=request.POST["scheduleData[" + str(i) + "][category]"],
            location=request.POST["scheduleData[" + str(i) + "][location]"],
            start=request.POST["scheduleData[" + str(i) + "][start]"],
            end=request.POST["scheduleData[" + str(i) + "][end]"],
            isAllDay=request.POST["scheduleData[" + str(i) + "][isAllDay]"],
            state=request.POST["scheduleData[" + str(i) + "][state]"],
            calendarClass=request.POST["scheduleData[" + str(i) + "][class]"],
        )
    return HttpResponse("강의 일정 저장 완료!")


# 학생,교수 기능 공유 부분
# 공통 부분 : 강의 일정 삭제
def deleteCalendars(request):
    if request.method == "POST":
        # print(request.POST)
        if request.session["userType"] == "student":
            for i in range(int(len(request.POST) / 7)):
                title = request.POST["array[" + str(i) + "][name]"]
                new_instance = Calendar.objects.filter(
                    userID=request.session["userID"], title=title
                )
                new_instance.delete()
            return HttpResponse("db와 일정 데이터 삭제 성공")
        elif request.session["userType"] == "professor":
            title = request.POST["title"]
            cal_Pdel = Calendar.objects.filter(
                userID=request.session["userID"], title=title
            )

            try:
                lec_del = Student_lecture.objects.filter(
                    professor=request.session["userName"], name=title
                )

                for i in range(lec_del.count()):
                    for j in range(cal_Pdel.count()):
                        cal_Sdel = Calendar.objects.filter(
                            userID=lec_del[i].student_id,
                            title=title,
                            start=cal_Pdel[j].start,
                            end=cal_Pdel[j].end,
                        )
                        cal_Sdel.delete()

            except lec_del.DoesNotExist:
                a = "aa"

            cal_Pdel.delete()

            return HttpResponse("db와 일정 데이터 삭제 성공")


# 공유 캘린더 부분 기능들
# 공유 캘린더용 calId 보내주는 부분
def pubCalSetData(request):
    pubCalSetData = PubCalID.objects.all()

    return HttpResponse(
        serializers.serialize("json", pubCalSetData), content_type="application/json"
    )


# 공유 캘린더 클릭시 교수의 강의 불러옴
def pro_lecture(request):
    if request.method == "POST":
        professor = Professor.objects.get(userID=request.session["userID"])
        data = Subject.objects.filter(
            professor=professor.username, department=professor.department
        )
        return HttpResponse(
            serializers.serialize("json", data), content_type="application/json"
        )


# 공용 일정 저장하는 함수
def pubCalSave(request):
    lecCode = request.POST["code"]  # request에서 온 강의 코드로 가정
    calID = "낮음"
    stdLecData = Student_lecture.objects.filter(code=lecCode)
    # print("request에서 온 강의를 듣는 학생들의 쿼리셋", stdLecData)
    subjectCount = Subject.objects.filter(code=lecCode)[0].stdCount + 1  # +1은 교수 카운트
    # print("subject 수강 인원 : ", subjectCount)

    end_date = datetime.datetime.strptime(
        request.POST["end"], "%Y-%m-%d"
    ).date()  # end데이터 date type으로 변환.
    end_date = end_date + datetime.timedelta(
        days=1
    )  # end데이터 +1(끝 날짜의 일정을 불러오지못하여 +1을 해주어 끝 날짜의 일정을 불러오기 위해)

    pubCalData = Calendar.objects.filter(userID="NULL")  # 초기화
    for data in stdLecData:  # 강의를 듣는 학생들의 공개 일정을 가져오는 쿼리 생성
        pubCalData = pubCalData | Calendar.objects.filter(
            userID=data.student_id, start__range=[request.POST["start"], end_date],
        )
        # print("필터링 데이터 : ", pubCalData[0].userID)
        # print(data.student_id) # 학생의 id값

    # 교수의 일정도 가져옴
    pubCalData = pubCalData | Calendar.objects.filter(
        userID=request.session["userID"],
        start__range=[request.POST["start"], end_date],
    )
    tmpData = pubCalData

    pubCalData = pubCalData.values("start", "end").annotate(count=Count("start"))

    # 데이터 초기화
    beforeData = PubCalendar.objects.filter(code=lecCode)
    beforeData.delete()

    # 해당 일정에 일정이 있는 학생 이름 저장
    for i in pubCalData:
        pubUserData = tmpData.filter(start=i["start"], end=i["end"]).distinct()
        userStr = ""
        for j in pubUserData:
            stdNameData = Student.objects.filter(userID=j.userID)
            for k in stdNameData:
                userStr += k.username + ", "
        for a in pubUserData:
            professorNameData = Professor.objects.filter(userID=a.userID).distinct()
            for k in professorNameData:
                userStr += k.username + ", "

        userStr = userStr[:-2]  # 마지막 쉼표 제거
        if i["count"] / subjectCount > 0.7:
            calID = "매우 높음"
        elif i["count"] / subjectCount > 0.5:
            calID = "높음"
        else:
            calID = "낮음"
        PubCalendar.objects.create(
            code=lecCode,
            calendarId=calID,
            title=str(i["count"]) + "명 일정 있음",
            start=i["start"],
            end=i["end"],
            count=i["count"],
            countPer=i["count"] / subjectCount,
            attendees=userStr,
        )

    return HttpResponse("일정 저장 완료.")


# 공유 캘린더 불러오기 버튼
def pubCalLoad(request):
    lecCode = request.POST["code"]

    end_date = datetime.datetime.strptime(request.POST["end"], "%Y-%m-%d").date()
    end_date = end_date + datetime.timedelta(days=1)

    pubCalData = PubCalendar.objects.filter(
        code=lecCode, start__range=[request.POST["start"], end_date]
    )

    return HttpResponse(
        serializers.serialize("json", pubCalData), content_type="application/json"
    )


# 공유 캘린더 과목 코드별 전체 수강생 정보 반환
def getAllStudent(request):
    student_list = Student_lecture.objects.filter(code=request.POST["code"])
    stores_list = Student.objects.filter(userID="Null")

    for i in range(student_list.count()):
        student_lifo = Student.objects.filter(userID=student_list[i].student_id)
        stores_list = stores_list | student_lifo

    return HttpResponse(
        serializers.serialize("json", stores_list), content_type="application/json"
    )


# 투표가능 시간대 출력
def voteTimeLoad(request):
    lecCode = request.POST["code"]
    start = request.POST["start"]
    end = request.POST["end"]

    start_date = datetime.datetime.strptime(request.POST["start"], "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(request.POST["end"], "%Y-%m-%d").date()
    end_date = end_date + datetime.timedelta(days=1)

    date_count = (end_date - start_date).days  # 날짜 수 (int형)

    pub_data = PubCalendar.objects.filter(
        code=lecCode, start__range=[start_date, end_date]
    )

    time = [
        "09:30:00",
        "10:45:00",
        "11:00:00",
        "12:15:00",
        "13:00:00",
        "14:15:00",
        "14:30:00",
        "15:45:00",
        "16:00:00",
        "17:15:00",
        "17:30:00",
        "18:45:00",
        "19:00:00",
        "20:15:00",
    ]
    for x in range(len(time)):
        time[x] = datetime.datetime.strptime(time[x], "%H:%M:%S").time()

    ava_time_list = []  # 빈 시간대들이 들어갈 리스트
    status_list = []  # 사용빈도가 들어갈 리스트

    if pub_data.exists():
        day = start_date
        for i in range(date_count):  # ex) 2020-11-01 ~ 2020-11-10
            # print(day)
            for j in range(int(len(time) / 2)):  # 하루의 교시 시간대들
                day_time_start = datetime.datetime.combine(
                    day, time[j * 2]
                )  # 받은 날짜와 고정된 시간을 datetime으로 결합
                day_time_end = datetime.datetime.combine(day, time[j * 2 + 1])
                # print(day_time_start)
                # print(day_time_end)

                pub = PubCalendar.objects.filter(
                    start__range=[day_time_start, day_time_end]
                )

                if pub:  # pubCalendar에 일정이 있다면
                    check = ""
                    check_index = 0
                    countPer = 0.0
                    for t in range(len(pub)):
                        if (
                            pub[t].calendarId == "매우 높음"
                        ):  # calendarId가 매우 높음으면 빨간색이므로 제외
                            check = ""
                            break
                        else:
                            check = "check"
                            if t == 0:
                                countPer = pub[t].countPer
                                check_index = t
                            else:
                                if countPer < pub[t].countPer:
                                    countPer = pub[t].countPer
                                    check_index = t
                    if check == "check":  # 빨간색을 제외한 회색과 노란색이 해당, 두 배열에 시간대와 사용빈도를 넣어줌
                        ava_time_list.append(
                            day_time_start.strftime("%Y-%m-%d %H:%M:%S")
                        )
                        ava_time_list.append(day_time_end.strftime("%Y-%m-%d %H:%M:%S"))
                        status_list.append(round(1.0 - pub[check_index].countPer, 2))
                elif not pub:  # 아무도 일정이 없는 시간대
                    ava_time_list.append(day_time_start.strftime("%Y-%m-%d %H:%M:%S"))
                    ava_time_list.append(day_time_end.strftime("%Y-%m-%d %H:%M:%S"))
                    status_list.append(1.0)
            day = day + datetime.timedelta(days=1)

        # print(ava_time_list)
        # print(status_list)

        send_dict = {"code": lecCode, "date": ava_time_list, "status": status_list}

        # print(send_dict)

        return HttpResponse(
            dumps(send_dict), content_type="application/json"
        )  # 파이썬 내장 json.dumps()로 json포맷 데이터 만듬
    else:
        return HttpResponse("공용 일정이 없습니다")


# ava_Time 테이블에 저장하고, 저장한 값을 보내줌
def voteTimeSave(request):
    # print(request.POST)
    ava_time = Ava_Time.objects.filter(classCode=request.POST["newDate[0][code]"])

    if request.method == "POST":
        if ava_time.exists():
            ava_time.delete()
        for i in range(int(len(request.POST) / 3)):
            new_instance = Ava_Time.objects.create(
                classCode=request.POST["newDate[" + str(i) + "][code]"],
                status=request.POST["newDate[" + str(i) + "][status]"],
                avaTime=request.POST["newDate[" + str(i) + "][date]"],
            )

            new_instance.save()

        order_table = ava_time.order_by("-status")

        return HttpResponse(
            serializers.serialize("json", order_table), content_type="application/json"
        )


# 해당 과목코드에 맞는 투표정보 반환
def getVoteInfo(request):
    voteInfo = Vote.objects.filter(classCode=request.POST["code"])

    return HttpResponse(
        serializers.serialize("json", voteInfo), content_type="application/json"
    )


def lec_Check(request):
    if request.method == "POST":
        test = Student_lecture.objects.filter(
            code=request.POST["code"], professor=request.session["userName"]
        )

    return HttpResponse(
        serializers.serialize("json", test), content_type="application/json"
    )


# 투표 개설
def create_Vote(request):
    if request.method == "POST":
        lecType = request.POST.get("select_Array[0][lecType]", False)
        className = request.POST.get("select_Array[0][className]", False)
        today_data_vote = request.POST["today"]
        start = request.POST["start"]
        end = request.POST["end"]
        status = ""

        convert_date_data = datetime.datetime.strptime(
            today_data_vote, "%Y-%m-%d %H:%M:%S.%f"
        )
        convert_date_start = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S.%f")
        convert_date_end = datetime.datetime.strptime(end, "%Y-%m-%d %H:%M:%S.%f")

        vote_all_info = Vote.objects.all()

        if convert_date_data < convert_date_start:
            status = "투표 전"
        elif (
            convert_date_data >= convert_date_start
            and convert_date_data <= convert_date_end
        ):
            status = "투표 중"
        elif convert_date_data > convert_date_end:
            status = "투표 마감"

        ava_Time1 = request.POST.get("select_Array[0][ava_Time]", False)
        ava_Time2 = request.POST.get("select_Array[1][ava_Time]", False)
        ava_Time3 = request.POST.get("select_Array[2][ava_Time]", False)
        ava_Time4 = request.POST.get("select_Array[3][ava_Time]", False)

        subject = Subject.objects.get(
            name=className, professor=request.session["userName"]
        )

        new_Vote = Vote.objects.create(
            classCode=request.POST["classCode"],
            lecType=lecType,
            proName=request.session["userName"],
            className=className,
            voteStatus=status,
            start=request.POST["start"],
            end=request.POST["end"],
            totalCount=subject.stdCount,
            choice1_Title=ava_Time1,
            choice2_Title=ava_Time2,
            choice3_Title=ava_Time3,
            choice4_Title=ava_Time4,
        )

        test = Vote.objects.all()

    return HttpResponse(
        serializers.serialize("json", test), content_type="application/json"
    )


# 투표 삭제
def delete_Vote(request):
    if request.method == "POST":
        classCode = request.POST["code"]

        delete_vote = Vote.objects.get(classCode=classCode)

        if delete_vote:
            infoKey = delete_vote.id
            # print(infoKey)
            deleteVoteInfo = VoteInfo.objects.filter(voteId=infoKey)
            deleteVoteInfo.delete()

        delete_vote.delete()

        test = Vote.objects.all()

    return HttpResponse(
        serializers.serialize("json", test), content_type="application/json"
    )


def check_Vote(request):
    if request.method == "POST":
        test = Vote.objects.all()

    return HttpResponse(
        serializers.serialize("json", test), content_type="application/json"
    )


# 강의가 있는지 확인
def check_user_subject(request):
    if request.session["userType"] == "student":  # 학생 강의 확인
        if Student_lecture.objects.filter(student_id=request.session["userID"]):
            return HttpResponse("강의 있음")
        else:
            return HttpResponse("강의 없음")
    else:  # 교수 강의 확인
        if Subject.objects.filter(professor=request.session["userName"]):
            return HttpResponse("강의 있음")
        else:
            return HttpResponse("강의 없음")


def pro_vote_update_table(request):
    if request.method == "POST":
        stores_list = Ava_Time.objects.filter(classCode=request.POST["classCode"])

    return HttpResponse(
        serializers.serialize("json", stores_list), content_type="application/json"
    )


def pro_vote_info(request):
    if request.method == "POST":
        stores_list = Vote.objects.filter(classCode=request.POST["classCode"])

    return HttpResponse(
        serializers.serialize("json", stores_list), content_type="application/json"
    )


# 투표 수정
def update_Vote(request):
    if request.method == "POST":
        lecType = request.POST["lecType"]
        className = request.POST["className"]
        today_data_vote = request.POST["today"]
        start = request.POST["start"]
        end = request.POST["end"]
        status = ""

        convert_date_data = datetime.datetime.strptime(
            today_data_vote, "%Y-%m-%d %H:%M:%S.%f"
        )
        convert_date_start = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S.%f")
        convert_date_end = datetime.datetime.strptime(end, "%Y-%m-%d %H:%M:%S.%f")

        vote_all_info = Vote.objects.all()

        if convert_date_data < convert_date_start:
            status = "투표 전"
        elif (
            convert_date_data >= convert_date_start
            and convert_date_data <= convert_date_end
        ):
            status = "투표 중"
        elif convert_date_data > convert_date_end:
            status = "투표 마감"

        ava_Time1 = request.POST.get("select_Array[0][ava_Time]", False)
        ava_Time2 = request.POST.get("select_Array[1][ava_Time]", False)
        ava_Time3 = request.POST.get("select_Array[2][ava_Time]", False)
        ava_Time4 = request.POST.get("select_Array[3][ava_Time]", False)

        deleteVote = Vote.objects.filter(
            proName=request.session["userName"], className=request.POST["className"]
        )

        if deleteVote:
            infoKey = deleteVote[0].id
            # print(infoKey)
            deleteVoteInfo = VoteInfo.objects.filter(voteId=infoKey)
            deleteVoteInfo.delete()

        deleteVote.delete()

        subject = Subject.objects.get(
            name=className, professor=request.session["userName"]
        )

        new_Vote = Vote.objects.create(
            classCode=subject.code,
            lecType=lecType,
            proName=request.session["userName"],
            className=className,
            voteStatus=status,
            start=request.POST["start"],
            end=request.POST["end"],
            totalCount=subject.stdCount,
            choice1_Title=ava_Time1,
            choice2_Title=ava_Time2,
            choice3_Title=ava_Time3,
            choice4_Title=ava_Time4,
        )

        test = Vote.objects.all()

    return HttpResponse(
        serializers.serialize("json", test), content_type="application/json"
    )


# 투표 확정2 (캘린더에 일정 생성 및 확정 관련 처리)
def createExamData(request):

    # print(request.POST["title"])

    startIdx = request.POST["title"].find("(")
    endIdx = request.POST["title"].find(")")

    subCode = (request.POST["title"])[startIdx + 1 : endIdx]
    # print(subCode)

    stdList = Student_lecture.objects.filter(code=subCode)

    new_instance = Calendar.objects.create(
        userID=request.session["userID"],
        calendarId=request.POST["calendarId"],
        title=request.POST["title"],
        category=request.POST["category"],
        location=request.POST["location"],
        start=request.POST["start"],
        end=request.POST["end"],
        isAllDay=request.POST["isAllDay"],
        state=request.POST["state"],
        calendarClass=request.POST["class"],
    )

    for std in stdList:
        new_instance = Calendar.objects.create(
            userID=std.student_id,
            calendarId=request.POST["calendarId"],
            title=request.POST["title"],
            category=request.POST["category"],
            location=request.POST["location"],
            start=request.POST["start"],
            end=request.POST["end"],
            isAllDay=request.POST["isAllDay"],
            state=request.POST["state"],
            calendarClass=request.POST["class"],
        )

    deleteVote = Vote.objects.get(classCode=subCode)
    deleteVoteInfo = VoteInfo.objects.filter(voteId=deleteVote.id)
    deleteVote.delete()

    if deleteVoteInfo:
        deleteVoteInfo.delete()

    return HttpResponse("저장 성공")


# 투표정보를 모두 불러 와서 시간비교하여 투표상태 바꾸기 위함.
def renewal_vote_status(request):
    if request.method == "POST":
        vote_all_info = Vote.objects.all()
        today_data_vote = request.POST["today"]

        # 오늘날짜를 테이블날짜형식에 맞춤
        convert_date_data = datetime.datetime.strptime(
            today_data_vote, "%Y-%m-%d %H:%M:%S.%f"
        )
        for i in range(vote_all_info.count()):
            if convert_date_data > vote_all_info[i].end:
                Vote.objects.filter(classCode=vote_all_info[i].classCode).update(
                    voteStatus="투표 마감",
                )

    return HttpResponse(
        serializers.serialize("json", vote_all_info), content_type="application/json"
    )


def student_voteTable(request):
    if request.method == "POST":
        stdID = request.session["userID"]
        stdLecture = Student_lecture.objects.filter(student_id=stdID)

        result = Vote.objects.filter(className="Null")

        for i in range(stdLecture.count()):
            if (
                request.POST["lecture_type"] == "전체"
                and request.POST["vote_status"] != "전체"
            ):
                stores_list = Vote.objects.filter(
                    className=stdLecture[i].name,
                    voteStatus=request.POST["vote_status"],
                )
            elif (
                request.POST["lecture_type"] != "전체"
                and request.POST["vote_status"] == "전체"
            ):
                stores_list = Vote.objects.filter(
                    className=stdLecture[i].name, lecType=request.POST["lecture_type"],
                )
            elif (
                request.POST["lecture_type"] == "전체"
                and request.POST["vote_status"] == "전체"
            ):
                stores_list = Vote.objects.filter(className=stdLecture[i].name)
            else:
                stores_list = Vote.objects.filter(
                    className=stdLecture[i].name,
                    lecType=request.POST["lecture_type"],
                    voteStatus=request.POST["vote_status"],
                )

            result = result | stores_list

    return HttpResponse(
        serializers.serialize("json", result), content_type="application/json"
    )


# 코멘트 가져오기
def bring_Comment(request):
    if request.method == "POST":
        # 과목코드를 받아옴
        classcode = request.POST["code"]
        # print(classcode)

        # vote테이블내의 과목코드를 비교하여 해당되는 쿼리셋을 불러옴.
        filt_vote_classcode = Vote.objects.get(classCode=classcode)
        # print(filt_vote_classcode)
        # ex) nn번 vote쿼리셋

        # vote테이블의 id로 필터링하여 votrinfo테이블에서 가져오기
        filt_voteid = VoteInfo.objects.filter(voteId=filt_vote_classcode.id,)

        # print(filt_voteid)

        return HttpResponse(
            serializers.serialize("json", filt_voteid), content_type="application/json"
        )


# 코멘트에 대한 학생 이름 가져오기
def bring_StdName(request):
    # print(request.POST)

    finalData = Student.objects.filter(userID="Null")  # 초기화

    for i in range(int(len(request.POST))):
        # print()
        finalData = finalData | Student.objects.filter(
            userID=request.POST["array[" + str(i) + "][studentID]"]
        )

    return HttpResponse(
        serializers.serialize("json", finalData), content_type="application/json"
    )

